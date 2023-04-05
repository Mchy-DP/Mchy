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

<fieldset><legend>Terminal</legend>
  
  ```bash
  $ .\compile.sh
  ...
  ERROR: The read-only variable `let apple_count: int` cannot be assigned to.
  ```

</fieldset>




Variables defined let must be given a value during creation. Some variables may be of compile constant type, indicated by the type being suffixed with a `!` Symbol. These variables are also implicitly read-only even if I was used to define them. For more information see the typing section.


