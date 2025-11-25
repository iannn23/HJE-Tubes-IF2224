class ASTNode:
   def __init__(self):
      self.semantic_type = None  #tipe data
      self.tab_index = None #reference ke symbol table (index)
      self.level = None #scope level

   def __repr__(self):
      return self.__class__.__name__
   
class ProgramNode(ASTNode):
   def __init__(self, name, declarations, block):
      super().__init__()
      self.name = name
      self.declarations = declarations
      self.block = block

#declaration
class VarDeclNode(ASTNode):
   def __init__(self, var_names, var_type):
      super().__init__()
      self.var_names = var_names
      self.var_type = var_type

#statement
class BlockNode(ASTNode):
   def __init__(self, statements):
      super().__init__()
      self.statements = statements

class AssignNode(ASTNode):
   def __init__(self, target, value):
      super().__init__()
      self.target = target
      self.value = value

class ProcCallNode(ASTNode):
   def __init__(self, name, args):
      super().__init__()
      self.name = name
      self.args = args


#expresion
class BinOpNode(ASTNode):
   def __init__(self, left, op, right):
      super().__init__()
      self.left = left
      self.op = op
      self.right = right



#leaf node
class NumberNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value   

class VarNode(ASTNode):
    def __init__(self, name):
        super().__init__()
        self.name = name             

class StringNode(ASTNode):
    def __init__(self, value):
        super().__init__()
        self.value = value