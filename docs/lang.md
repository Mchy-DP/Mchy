# Language Specification

This file documents the language features of mchy, For specific functions and properties see the [libraries](/docs/home.md).  The examples in this file, unless otherwise noted, will assume that the [standard library](/docs/libs/std.md) is available (Thus functions like print can be used to demonstrate the workings of code structures)

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

Variable can also be assigned to during creation by adding equals followed by an expression afterwards. 
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
    print("Too many ninja's, Retreat!")
}
```
Elif blocks can be added to an if.  These blocks will only execute if their condition resolves True and all preceding conditions resolved false.
```py
var ninja_count: int = 17:
if ninja_count > 11{
    print("Too many ninja's, Retreat!")
} elif ninja_count == 0 {
    print("It's quiet... too quiet...")
}
```
An else block can be appended to the end of a if/elif block.  It will only execute if all other condtions resolved False
```py
var ninja_count: int = 17:
if ninja_count > 11{
    print("Too many ninja's, Retreat!")
} elif ninja_count == 0 {
    print("It's quiet... too quiet...")
} else {
    print("We can take em, Charge!")
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
While loops will continue to execute the loop body until the condition resolves false.

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
Most functions expect arguments, which can be set by passing values to them
```py
print("Well hello there!")
```
Some functions, like print, can accept any number of arguments.
```py
print("Well ", "hello ", "there!")
```
Some arguments may have a default value thus making them optional.
### Executors
Many functions need to run on an entity/player, To do this first get the entity (see: [.get_entities()](/docs/libs/std.md#get_entities) from the standard library).  Then you can run the function on it via dot accessing:

```py
let random_player: Player = world.get_player("random").find()

random_player.say("I was randomly picked!")
```

## Properties & Chains
### Properties
Properties are almost identical to functions except that they need no arguments.  As a result they are used in the same way except that the `(...)` must be ommited:
```py
let compiler_version: int = world.version
```

### Chains
Sometimes library methods & properties may not return a complete type (such as an int or Player) instead they only make sense if further methods or properties are used to clarify the command.  These are called method/property chains.  One example of such a chain was shown above, The `get_entities()` function.
```py
let random_player: Player = world.get_player("random").find()
```
note here that `world.get_player("random")` does not actually do anything instead it is a partial entity selector.  When `.find()` is called only then is it a real type (A `Player` in this case) which can be stored to a variable.

In the case of `get_player()` the reason that it is a partial selector rather than a player is that further filters can be added.  For instance:
```
let random_player_at_level_30: Player = world.get_player("random").with_level(min=30, max=1000000).find()

random_player_at_level_30.say("I'm at level 30!")
```

## Arithmetic & Comparison Operations

## Misc
### Comments
### Raw Commands
### Structs
## Typing
WIP