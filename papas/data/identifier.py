# simplified class to provide a unique identifier for each object
# could also add more information into the identifier as needed
class Identifier(long):
    '''the Identififier is a uniqueid that contains encoded information about an element
           for example, given an indentifier, we can determine that the element is an ecal_cluster
           and retrieve the cluster from a cluster dict.
    
        The Identifier class consists of a set of static methods that can be used
        to create and to dissect identifiers.
        
        The first(rightmost) 40 bits are used to contain the python unique objectid of the item
        The bits to the left of this contain the objecttype eg ECALCLUSTER etc
        
        usage:
           self.uniqueid = Identifier.make_id(self,Identifier.PFOBJECTTYPE.BLOCK) 
           if Identifier.is_track(self.uniqueid):
                ....
           
        '''    
    class PFOBJECTTYPE:
        NONE = 0
        ECALCLUSTER = 1 #simplistic initial implementation (may need an enum for layer to be added)
        HCALCLUSTER = 2
        TRACK = 3
        PARTICLE = 4
        RECPARTICLE = 5
        BLOCK = 6
    
    @staticmethod    
    def make_id(item, type):
        x = id(item) #COLIN replace by static counter 
        value = type <<40
        return value | x
   
    @staticmethod      
    def get_unique_id( ident):
        return ident & 0b1111111111111111111111111111111111111111
    
    @staticmethod  
    def get_type ( ident):
        return ident >> 40
    
    @staticmethod  
    def is_ecal ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.ECALCLUSTER  

    @staticmethod  
    def is_hcal ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.HCALCLUSTER  

    @staticmethod  
    def is_track ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.TRACK 
    
    @staticmethod  
    def is_block ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.BLOCK     
    
    @staticmethod  
    def is_rec_particle ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.RECPARTICLE 
    
    @staticmethod  
    def is_particle ( ident):
        return Identifier.get_type(ident)  == Identifier.PFOBJECTTYPE.PARTICLE     
    
    @staticmethod
    def type_short_code(ident):
        typelist=".eht......" #the enum value (0 to 8) will index into this and return E is it is ECAL etc
        return typelist[Identifier.get_type(ident)]    
    
    
    
