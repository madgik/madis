import setpath
import cPickle
import functions



class piv:
    """
    UFO: Unidentified Function Operator
    """
    #registered=True

    def __init__(self):
        self.initialized=False
        self.pivinfo=None
        pass

    def parseargs(self,*args):
        if len(args)<5:
            raise functions.OperatorError("pivotop","not valid arguments: number of args:%s\n args: %s" %(len(args),str(args)))
        if not self.initialized:
            self.initialized=True
            try:
                self.pivinfo=cPickle.loads(str(args[0].strip('"\'')))
                self.output=['']*self.pivinfo.getsize()
            except cPickle.UnpicklingError:
                raise functions.OperatorError("pivotop","first argument not valid")
            if args[1]!="piv":
                raise functions.OperatorError("pivotop","arguments not valid: piv position")
            self.pivpos=2
            try:
                self.opspos=args.index("ops")+1
            except ValueError:
                raise functions.OperatorError("pivotop","arguments not valid: ops position")
        return (args[self.pivpos:self.opspos-1],args[self.opspos:])

    def step(self, *args):
        #piv(pickled pivotel in quotes,"piv",pivcolval,"ops",opcolval)
                
        valist,opslist=self.parseargs(*args) 
        for oppos in xrange(len(opslist)):
            self.output[self.pivinfo.getvalposition(valist,oppos)]=opslist[oppos]



    def final(self):
        from lib.buffer import CompBuffer
        a=CompBuffer()
        a.writeheader(self.pivinfo.getcolnames())
        a.write(self.output)
        return a.serialize()






