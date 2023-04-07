# Language Specification

This file documents the language features of mchy, For specific functions and properties see the [libraries](/docs/home.md).  The examples in this file, unless otherwise noted, will assume that the [standard library](/docs/libs/std.md) is available (thus functions like `print` can be used to demonstrate the workings of code structures).

## Variables
### Var
Variables can be created (instantiated) with the var keyword.  A type must also be specified during the variables creation.
```py
var apple_count: int
```

Once a variable is created it can be used freely without having to re-specify the type or use the Var keyword.
```py
var apple_count: int
apple_count = 5 + 4
print("I counted ", apple_count, " apples, I expected to count 9!")
```

Variables can also have values assigned to them during creation by adding equals followed by an expression afterwards.
```py
var apple_count: int = 5 + 4
print("I counted ", apple_count, " apples, I expected to count 9!")
```

### Let
Variables can also be instantiated using the keyword let.
```py
let apple_count: int = 5 + 4
print("I counted ", apple_count, " apples, I expected to count 9!")
```

When variables are instantiated with the keyword let they are read-only and attempts to modify their value will raise an error during compilation.
```py
let apple_count: int = 5
apple_count = apple_count + 4
print("I counted ", apple_count, " apples, I expected to count 9!")
```
> Terminal:
> ```bash
> $ .\compile.sh
> ...
> ERROR: The read-only variable `let apple_count: int` cannot be assigned to.
> ```

Variables defined by let must be given a value during creation. 
```py
let apple_count: int
apple_count = 5 + 4
print("I counted ", apple_count, " apples, I expected to count 9!")
```
> Terminal:
> ```bash
> $ .\compile.sh
> ...
> ERROR: Read only (let) variables must be assigned to on declaration.
> ```

### Constant typed variables
Some variables may be of compile constant type, indicated by the type being suffixed with a `!` Symbol.
```py
let apple_count: int! = 5 + 4
print("I counted ", apple_count, " apples, I expected to count 9!")
```
These variables are also implicitly read-only even if `var` was used to define them. For more information see the [typing](#typing) section.

## If-Elif-Else

If statements can be used to execute some code only if a condition is met:
```py
var ninja_count: int = 17:
if ninja_count > 11{
    print("Too many ninjas: Retreat!")
}
```
Elif blocks can be added to an if.  These blocks will only execute if their condition resolves True and all preceding conditions resolved False.
```py
var ninja_count: int = 17:
if ninja_count > 11{
    print("Too many ninjas: Retreat!")
} elif ninja_count == 0 {
    print("It's quiet... too quiet...")
}
```
An else block can be appended to the end of a if/elif block.  It will only execute if all other conditions resolved False.
```py
var ninja_count: int = 17:
if ninja_count > 11{
    print("Too many ninjas: Retreat!")
} elif ninja_count == 0 {
    print("It's quiet... too quiet...")
} else {
    print("We can take em: Charge!")
}
```

## Loops
### While
While loops are supported with the following syntax:
```py
while <condition> {
    <loop body>
}
```
While loops will continue to execute the loop body until the condition resolves False.

Example while loop:
```py
var count: int = 0
print("Starting loop")
while (count < 5) {
    print("On iteration ", count)
    count = count + 1
}
print("Finished loop")
```
> Minecraft Chat:
> ```txt
> Starting loop
> On iteration 0
> On iteration 1
> On iteration 2
> On iteration 3
> On iteration 4
> Finished loop
> ```


### For
For loops are also supported.  They use the following syntax:
```py
for <index_var> in <lower_bound>..<upper_bound> {
    <loop body>
}
```

For loops run the loop body once for every integer between the `lower_bound` and `upper_bound` they also automatically create the `index_var` and set it to the integer associated with the current loop.

Example for loop:
```py
print("Starting loop")
for count in 0..4{
    print("On iteration ", count)
}
print("Finished loop")
```
> Minecraft Chat:
> ```txt
> Starting loop
> On iteration 4
> On iteration 3
> On iteration 2
> On iteration 1
> On iteration 0
> Finished loop
> ```

## Functions
### Simple function calls
Functions can be called by writing the function name followed by `()`
```py
# Print a blank line to chat
print()
```
Most functions expect arguments, which can be set by passing values to them.
```py
print("Well hello there!")
```
Some functions, like print, can accept any number of arguments.
```py
print("Well ", "hello ", "there!")
```
Some arguments may have a default value thus making them optional.
### Executors
Many functions need to run on an entity/player. To do this first get the entity (see: [.get_entities()](/docs/libs/std.md#get_entities) from the standard library).  then you can run the function on it via dot accessing:

```py
let random_player: Player = world.get_player("random").find()

random_player.say("I was randomly picked!")
```

### Defining functions
You can define your own functions in the simplest case with the following syntax:
```py
def <func_name>(){
    <func_body>
}
```
Where `func_name` is the name of the new function and `func_body` are the statements to execute when the function is called. E.g.
```py
def print_answer(){
    print("The answer is: ", 42)
}
print_answer()
```
You can add arguments between the parentheses, arguments must have a type.
```py
def print_answer(number: int){
    print("The answer is: ", number)
}
print_answer(13)
```
You can also provide a default value which will be used if the user provides no value.
```py
def print_answer(number: int = 42){
    print("The answer is: ", number)
}
print_answer(13)
print_answer()
```
> Minecraft Chat:
> ```txt
> /reload
> The answer is: 13
> The answer is: 42
> ```

### Return
You can return values from functions:  Just add a return type to the end of the function signature and then write `return <value_to_return>` inside your function body.
```py
def get_answer() -> int{
    return 42
}
print("I got the answer: ", get_answer())
```
> Minecraft Chat:
> ```txt
> /reload
> I got the answer: 42
> ```

### Executors
You can require that a function execute on a specific executable type (see [typing](#typing)) by including that type after `def`:
```py
def Group[Entity] say_answer(){
    this.say("The answer is: 42!")
}

let player: Player = get_player("random").find()
player.say_answer()
```
> Minecraft Chat:
> ```txt
> /reload
> [USERNAME] The answer is: 42!
> ```

### Final syntax reference
With everything above added this give the final function definitions syntax as:
```py
def <ExecutorType> <func_name>(<param1_name>: <param1_type>, ...) -> <return_type> {
    <func_body>
}
```

## Properties & Chains
### Properties
Properties are almost identical to functions except that they need no arguments.  As a result they are used in the same way except that the `(...)` must be ommited:
```py
let compiler_version: int = world.version
```

### Chains
Sometimes library methods and properties may not return a complete type (such as an int or Player) instead they only make sense if further methods or properties are used to clarify the command.  These are called method/property chains.  One example of such a chain was shown above; the `get_entities()` function.
```py
let random_player: Player = world.get_player("random").find()
```
Note here that `world.get_player("random")` does not actually do anything, instead it is a partial entity selector.  When `.find()` is called only then is it a real type (A `Player` in this case) which can be stored to a variable.

In the case of `get_player()` the reason that it is a partial selector rather than a Player is that further filters can be added.  For instance:
```py
let random_player_at_level_30: Player = world.get_player("random").with_level(min=30, max=1000000).find()

random_player_at_level_30.say("I'm at level 30!")
```

## Arithmetic & Comparison Operations
| Name             | Syntax    | Description                                                             |
| -------------    | --------  | ----------------------------------------------------------------------- |
| Addition         | `X + Y`   | Yields the addition of `X` and `Y`                                      |
| Subtraction      | `X - Y`   | Subtracts `Y` from `X`                                                  |
| Multiplication   | `X * Y`   | Yields the product of `X` and `Y`                                       |
| Division         | `X / Y`   | Performs integer division on `X` by `Y`                                 |
| Modulo/Remainder | `X % Y`   | Yields the remainder of performing integer division between `X` and `Y` |
| Exponent         | `X ** Y`  | Raises `X` to the power of `Y`                                          |
| Equality         | `X == Y`  | Returns true if `X` is equal to `Y`                                     |
| Inequality       | `X != Y`  | Returns true if `X` is not equal to `Y`                                 |
| GTE              | `X >= Y`  | Returns true if `X` is greater than or equal to `Y`                     |
| GT               | `X >  Y`  | Returns true if `X` is greater than `Y`                                 |
| LTE              | `X <= Y`  | Returns true if `X` is less than or equal to `Y`                        |
| LT               | `X >  Y`  | Returns true if `X` is less than `Y`                                    |
| String Literal   | `"X"`     | Yields the literal string `X`                                           |
| Float Literal    | `3.14`    | Yields the literal float `3.14`                                         |
| Integer Literal  | `42`      | Yields the literal integer `42`                                         |
| Bool             | `true`    | Yields the literal boolean `true`, `false` also valid                   |
| Null Literal     | `null`    | Yields the literal value `null`                                         |
| World            | `world`   | Yields the world                                                        |
| This             | `this`    | Yields the executing entity in a function                               |
| Not              | `not X`   | Yields true if `X` is False and False if `X` is True                    |
| And              | `X and Y` | Yields true if both `X` and `Y` are True, False otherwise               |
| Or               | `X or Y`  | Yields true if either `X` or `Y` are True, False otherwise              |
| NullCoal         | `X ?? Y`  | Yields `X` if `X` is not null, `Y` otherwise.  `Y` cannot be null       |


## Misc
### Comments
Any line begining with a `#` symbol is a code comment and will not be executed.
```py
# Not a real line
print("Real line")
# print("This is a print that has been commented out so won't run!")
```
### Raw Commands
Any line starting with a `/` symbol will be directly inserted at that position into the output Datapack as a raw Minecraft command.
```py
print("About to force speech")
/execute as @a run say I decided to say this because a raw command made me do it!
print("Finished forcing speech!")
```
Note: If you want to build a raw command out of Compile-time constant Strings (`str!`) then use [`world.cmd(...)`](/docs/libs/std.md#cmd) from the standard library.
### Structs
Some functions & properties such as [`world.pos.constant(...)`](/docs/libs/std.md#constant) return compile-time structs.  These represent data structures more complicated than simple int's or str's are sufficient for.  Structs can usually be stored in variables.
```py
let selected_color: Color = world.colors.red
print("I am normal text, ", selected_color, "I am scary coloured text!")
```
### Decorators
Functions can be proceeded by `@<decorator>` to change/add behaviours of that function.
#### Ticking
The `@ticking` decorator can proceed any function that executes on world with no return type or parameters.  When the `@ticking` decorator is used the function will run once every 20th of a second.
```py
@ticking
def main_tick(){
    print("Spam chat 20 times a second!")
}
```
```py
var tick: int = 0

@ticking
def secondly(){
    tick = tick + 1
    if (tick % 20) == 0 {
        print("Spam chat once a second!")
    }
}
```
#### Public
The `@public` decorator can precede any function with no parameters.  When the `@public` decorator is used the function will be callable from in world via the `/function` command at the location `<file name>:generated/public/<function name>`.
```py
# In the file apple_prints.mchy
@public
def output_apples(){
    print("apples!")
}
```
> In Minecraft chat:
> ```MCDP
> /function apple_prints:generated/public/output_apples
> apples!
> ```
## Typing
There are 3 broad catagories of type in mchy: Inert types, Executable types & Struct Types.  Struct types are special types used by structures and minimal knowledge is needed about them, as such they will not be discussed here more than to acknowledge their existence.
### Inert Types
Inert types have 5 core subtypes that come under this heading: `float`, `int`, `bool`, `str` & `null`.  Inert types have 2 variants: nullable & compile constant.  These are indicated by adding the suffixes Indicated below.
| Property          | Suffix        |
| -------------     | ------------- |
| Nullable          | `?`           |
| Compile Constant  | `!`           |

#### Nullable
Any nullable type can, in addition to it's normally valid assignments, be assigned to null.  This allows for returning no-result values from functions.
```py
var a: int? = null
```
#### Compile Constant
Many operations are not possible at runtime due to the limitations of Minecraft Datapacks.  However sometimes it is enough to resolve a value at compile time.  For instance: The particle command has the following syntax:
```MCDP
/particle <name> [<pos>] [<delta>] <speed> <count> [force|normal]
```
This equates to the following Mchy command:
```py
particle(location: std::Pos, particle: str!, dx: float!, dy: float!, dz: float!, speed: float!, count: int!, force_render: bool! = False) -> null
```
The value `<speed>` must be a hard-coded float due to the underlying command.  However imagine that we have 10 different types of campfire added by a Datapack we are writing.  All these campfires use the flame particle to produce part of their effect and all should have the same speed of fire.  If we want to change the speed of the flame particles then traditionally we would have to edit all of the commands individually, however with constant types we can create a single constant variable to edit and change all of them at once.
```py
...
let flame_speed: float! = 0.05

world.particle(world.pos.constant(0,70,0), 0.1, 0.1, 0.1,  flame_speed, 40)
world.particle(world.pos.constant(0,70,0), 0.01,0.1, 0.01, flame_speed, 10)
world.particle(world.pos.constant(0,70,0), 1.5, 1.5, 1.5,  flame_speed, 100)
...
world.particle(world.pos.constant(0,70,0),-0.2,-0.1,-0.2,  flame_speed, 8)
```
