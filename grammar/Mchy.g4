grammar Mchy;

mchy_file: NEWLINE* top=top_level_scope NEWLINE* EOF;

top_level_scope: top_elems (stmnt_ending top_elems)*;

top_elems: (stmnt|function_decl);

stmnt: (expr|variable_decl|assignment|unary_stmnt|return_ln|if_stmnt|while_loop|for_loop|user_comment|raw_cmd);

function_decl: decorators=decorator_list def_kw=DEF (exec_type=type)? func_name=IDENTIFIER '(' params=param_decl_list? ')' (ARROW return_type=type)? body=scoped_code_block;

decorator_list: (decorator NEWLINE)*;

decorator: ATSIGN decorator_name=IDENTIFIER;

stmnt_ending: NEWLINE+;

raw_cmd: mc_cmd=RAW_CMD;

while_loop: WHILE condition=expr body=code_block;

for_loop: FOR index_var_name=IDENTIFIER IN lower_bound=for_range_bound DOT DOT upper_bound=for_range_bound body=code_block;

for_range_bound: (IDENTIFIER|INT|('(' expr ')'));

if_stmnt: IF condition=expr body=code_block (elif_comp=elif_stmnt)? (else_comp=else_stmnt)?;
elif_stmnt: ELIF condition=expr body=code_block (continuation=elif_stmnt)?;
else_stmnt: ELSE body=code_block;

scoped_code_block: block=code_block;
code_block: '{' (NEWLINE* stmnt (stmnt_ending stmnt)*)? NEWLINE* '}';

variable_decl: varkw=(VAR|LET) var_name=IDENTIFIER COLON var_type=type (EQUAL assignment_target=expr)?;

assignment: lhs=IDENTIFIER method=(EQUAL|PLUSEQUAL|MINUSEQUAL|MULTEQUAL|DIVEQUAL|MODEQUAL) rhs=expr;

unary_stmnt: target=IDENTIFIER operation=(PLUSPLUS|MINUSMINUS);

return_ln: RETURN target=expr;

user_comment: com_tok=COMMENT;

expr: '(' NEWLINE* contents=expr NEWLINE* ')'                                                                                               #ExprParen
    | executor=expr DOT func_name=IDENTIFIER '(' params=param_list? ')'                                                                     #ExprFuncCall
    | func_name=IDENTIFIER '(' params=param_list? COMMA? NEWLINE* ')'                                                                       #ExprWorldFuncCall
    | source=expr DOT attribute=IDENTIFIER                                                                                                  #ExprPropertyAccess
    | <assoc=right> base=expr ('^'|'*' '*') exponent=expr                                                                                   #ExprExponent
    | MINUS target=expr                                                                                                                     #ExprUnaryMinus
    | left=expr sign=('%'|'/'|'*') right=expr                                                                                               #ExprMultDivMod
    | left=expr sign=('+'|'-') right=expr                                                                                                   #ExprPlusMinus
    | left=expr comparison=(EQUALITY | INEQUALITY | COMP_LTE | COMP_LT | COMP_GTE | COMP_GT) right=expr                                     #ExprRelation
    | NOT target=expr                                                                                                                       #ExprNot
    | left=expr AND right=expr                                                                                                              #ExprAnd
    | left=expr OR right=expr                                                                                                               #ExprOr
    | opt_expr=expr QUESTION_MARK QUESTION_MARK default_expr=expr                                                                           #ExprNullCoalescing
    | value=DBQ_STRING                                                                                                                      #LiteralStrDBQ
    | value=SGQ_STRING                                                                                                                      #LiteralStrSGQ
    | value=NULL                                                                                                                            #LiteralNull
    | value=TRUE                                                                                                                            #LiteralTrue
    | value=FALSE                                                                                                                           #LiteralFalse
    | value=WORLD                                                                                                                           #LiteralWorld
    | value=THIS                                                                                                                            #LiteralThis
    | value=IDENTIFIER                                                                                                                      #LiteralIdent
    | value=FLOAT                                                                                                                           #LiteralFloat
    | value=INT                                                                                                                             #LiteralInt
    ;

param_list: param (COMMA param)*;
param: NEWLINE* (label=IDENTIFIER EQUAL)? value=expr NEWLINE*;

param_decl_list: param_decl (COMMA param_decl)*;
param_decl: param_name=IDENTIFIER COLON param_type=type (EQUAL default_value=expr)?;

type: ((core_type=(WORLD|IDENTIFIER|NULL) constant=BANG_MARK? nullable=QUESTION_MARK?) | (groupkw=GROUP '[' group_target=IDENTIFIER ']'));


fragment DIGIT: [0-9];
fragment LOWER_LETTER: [a-z];
fragment UPPER_LETTER: [A-Z];
fragment LETTER: (LOWER_LETTER|UPPER_LETTER);
fragment ALPHANUMERIC: (LETTER|DIGIT);

fragment DBQ_QESC: '\\' '"';
fragment SGQ_QESC: '\\' '\'';
DBQ_STRING: '"' (DBQ_QESC | ~["\n])*? '"';
SGQ_STRING: '\'' (SGQ_QESC | ~['\n])*? '\'';
FLOAT: DIGIT+ '.' DIGIT+;
INT: DIGIT+;
VAR: 'var';
LET: 'let';
DEF: 'def';
GROUP: 'Group';
NULL: 'null';
TRUE: 'true'|'True';
FALSE: 'false'|'False';
RETURN: 'return';
WORLD: 'world';
THIS: 'this';
IF: 'if';
ELIF: 'elif';
ELSE: 'else';
WHILE: 'while';
NOT: 'not';
AND: 'and';
OR: 'or';
FOR: 'for';
IN: 'in';
IDENTIFIER: (LETTER|'_')(ALPHANUMERIC|'_')*;


ARROW: '->';
EQUAL: '=';
PLUSEQUAL: '+=';
MINUSEQUAL: '-=';
MULTEQUAL: '*=';
DIVEQUAL: '/=';
MODEQUAL: '%=';
PLUSPLUS: '++';
MINUSMINUS: '--';
EQUALITY: '==';
INEQUALITY: '!=';
COMP_LTE: '<=';
COMP_LT: '<';
COMP_GTE: '>=';
COMP_GT: '>';
POPEN: '(';
PCLOSE: ')';
SBOPEN: '[';
SBCLOSE: ']';
CBOPEN: '{';
CBCLOSE: '}';
CARROT: '^';
STAR: '*';
PLUS: '+';
MINUS: '-';
SLASH: '/';
NEWLINE: '\n' {self.cust_hit_newline()}?;  // predicate used to support getting the distance into the line for tokens such as RAW_CMD
UNDERSCORE: '_';
DOT: '.';
ATSIGN: '@';
COMMA: ',';
QUESTION_MARK: '?';
BANG_MARK: '!';
COLON: ':';
COMMENT: '#' ~[\n]*;

RAW_CMD: ([ \t]*) '/' {((self.cust_get_index_into_line() - len(self.text)) == 0)}? ~[\n]*;

WS: [ \t] -> channel(HIDDEN);

UNKNOWN_CHAR: .;