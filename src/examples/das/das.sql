hidden var 'UKRN4prefixes1' from '\bdata\b|\bcode\b|\bmaterial\b|\bsoftware\b|\bstatement\b|\bartifact\b';
hidden var 'full_and_good' from 'freely available|public domain|data are open source|publicly available|accessible through the link|(available (?:at|via|through|to))|((?:have been|are|was|were) deposited)|available without restriction|(can be found(?:,? in the)? online)|can be downloaded|(access(?:ed|ible) (f?from|at))|available online from';
hidden var 'supplementary' from '(in appendi(?:x|ces))|study are included|in supplement(al (mat|info)|ary (mat|file))|within the (article|manuscript|paper)|are included in (the (article|paper)|this( published article)?)|supporting info|provided within|contained within|appear in the submitted article|all relevant data are within|data are included';
hidden var 'on_request' from 'made available by the authors|((?:upon|by|on|reasonable) request)|available from the corresponding author';
hidden var 'no_immediate_access' from '(third part(?:y|ies))|confidential|will be available following approval|are ?n.t shared publicly|cannot be shared publicly|do ?n.t have permission|personal information|sensitive info|sensitive nature|written consent|patient consent|data protection|protect anonym|protected data|cannot\sbe shared|after securing relevant permissions';
hidden var 'no_data' from'no (?:data|dataset|datasets|data ?sets) (?:was|were)? (?:used|produced|generated|collected|created|available)|not\sapplicable|no new data|data availability (?:statement)?[:\.]?\s*n\/a';


drop table DAStexts_last;
create table DAStexts_last as
select doi, middle, next, middle||" "||regexpr("\..+$",next,"") as textsnippet, middle||" "|| next as totaltext
from (setschema 'doi,prev,middle,next'
      select C3 as doi, textwindow2s(regexpr("\n",lower(C2)," "), 0, 1, 20, var('UKRN4prefixes1'))
      from (select * from txts))
where (regexprmatches("%{full_and_good}",middle||next) = 1 or
       regexprmatches("%{supplementary}",middle||next) = 1 or
       regexprmatches("%{on_request}",middle||next) = 1 or
       regexprmatches("%{no_immediate_access}",middle||next) = 1 or
       regexprmatches("%{no_data}",middle||next) = 1)
       and length(middle)-length(regexpr("("||var('UKRN4prefixes1')||")",middle)) < 3;


drop table DAStexts_with_categories_last;
create table DAStexts_with_categories_last as
select doi, textsnippet, totaltext,  "full and good" as category
from DAStexts_last
where doi in (select doi from DAStexts_last where regexprmatches("%{full_and_good}",textsnippet)) and  regexprmatches("not publicly available|available on|not", textsnippet) = 0
union all
select  doi, textsnippet, totaltext,  "supplementary" as category
from DAStexts_last
where doi in (select doi from DAStexts_last where regexprmatches("%{supplementary}",textsnippet))
union all
select doi, textsnippet, totaltext, "on_request" as category
from DAStexts_last
where doi in (select doi from DAStexts_last where regexprmatches("%{on_request}",textsnippet))
union all
select doi, textsnippet, totaltext,  "no_immediate_access" as category
from DAStexts_last
where doi in (select doi from DAStexts_last where regexprmatches("%{no_immediate_access}",textsnippet))
union all
select doi, textsnippet, totaltext,  "no_data" as category
from DAStexts_last
where doi in (select doi from DAStexts_last where regexprmatches("%{no_data}",textsnippet));
