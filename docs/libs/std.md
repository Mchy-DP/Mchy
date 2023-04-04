# std
## Functions
### area_replace
```
area_replace(pos1: std::Pos, pos2: std::Pos, old_block: str!, new_block: str!) -> null
```
### bool
```
bool(x: int) -> bool
```
### cmd
```
cmd(mc_cmd: str!) -> null
```
### effect_add
```
Entities.effect_add(effect: str!, seconds: int!, amplifier: int!, particles: bool! = True) -> null
```
### effect_clear
```
Entities.effect_clear(effect: str!? = null) -> null
```
### fill
```
fill(pos1: std::Pos, pos2: std::Pos, block: str!, mine_existing: bool! = False, keep_existing: bool! = False) -> null
```
### give
```
Players.give(item: str!, count: int!, data: str! = {}) -> null
```
### kill
```
Entities.kill() -> null
```
### particle
```
particle(location: std::Pos, particle: str!, dx: float!, dy: float!, dz: float!, speed: float!, count: int!, force_render: bool! = False) -> null
```
### play_sound
```
Players.play_sound(sound_location: std::Pos, sound: str!, channel: str! = master, volume: float! = 1.0, pitch: float! = 1.0, min_volume: float! = 0.0) -> null
```
### print
```
print() -> null
```
### say
```
say(msg: str!) -> null
```
### setblock
```
setblock(location: std::Pos, block: str!, mine_existing: bool! = False, keep_existing: bool! = False) -> null
```
### spread
```
Entities.spread(center: std::Pos, radius: float!, spacing: float! = 0.0, respect_teams: bool! = False, max_height: int!? = null) -> null
```
### summon
```
summon(location: std::Pos, entity_type: str!, nbt_data: str!? = null) -> Entity
```
### tag_add
```
Entities.tag_add(new_tag: str!) -> null
```
### tag_count
```
Entity.tag_count() -> int
```
### tag_remove
```
Entities.tag_remove(target_tag: str!) -> null
```
### tp
```
tp(target_location: std::Pos) -> null
```
## Properties
### version
```
version -> int
```
## Chained methods
* ### colors
  ```
  .colors
  ```
  * ### aqua
    ```
    .colors.aqua
    ```
  * ### black
    ```
    .colors.black
    ```
  * ### blue
    ```
    .colors.blue
    ```
  * ### cyan
    ```
    .colors.cyan
    ```
  * ### dark_aqua
    ```
    .colors.dark_aqua
    ```
  * ### dark_blue
    ```
    .colors.dark_blue
    ```
  * ### dark_gray
    ```
    .colors.dark_gray
    ```
  * ### dark_green
    ```
    .colors.dark_green
    ```
  * ### dark_purple
    ```
    .colors.dark_purple
    ```
  * ### dark_red
    ```
    .colors.dark_red
    ```
  * ### gold
    ```
    .colors.gold
    ```
  * ### gray
    ```
    .colors.gray
    ```
  * ### green
    ```
    .colors.green
    ```
  * ### hex
    ```
    .colors.hex
    ```
  * ### light_purple
    ```
    .colors.light_purple
    ```
  * ### lime
    ```
    .colors.lime
    ```
  * ### red
    ```
    .colors.red
    ```
  * ### white
    ```
    .colors.white
    ```
  * ### yellow
    ```
    .colors.yellow
    ```
* ### get_entities
  ```
  .get_entities
  ```
  * ### failing_predicate
    ```
    .get_entities.failing_predicate
    ```
  * ### find
    ```
    .get_entities.find
    ```
  * ### from_position
    ```
    .get_entities.from_position
    ```
  * ### in_radius
    ```
    .get_entities.in_radius
    ```
  * ### in_team
    ```
    .get_entities.in_team
    ```
  * ### in_volume
    ```
    .get_entities.in_volume
    ```
  * ### matching_nbt
    ```
    .get_entities.matching_nbt
    ```
  * ### not_in_team
    ```
    .get_entities.not_in_team
    ```
  * ### not_matching_nbt
    ```
    .get_entities.not_matching_nbt
    ```
  * ### of_name
    ```
    .get_entities.of_name
    ```
  * ### of_type
    ```
    .get_entities.of_type
    ```
  * ### passing_predicate
    ```
    .get_entities.passing_predicate
    ```
  * ### with_hrz_rot
    ```
    .get_entities.with_hrz_rot
    ```
  * ### with_no_team
    ```
    .get_entities.with_no_team
    ```
  * ### with_score
    ```
    .get_entities.with_score
    ```
  * ### with_tag
    ```
    .get_entities.with_tag
    ```
  * ### with_vert_rot
    ```
    .get_entities.with_vert_rot
    ```
  * ### without_tag
    ```
    .get_entities.without_tag
    ```
* ### get_entity
  ```
  .get_entity
  ```
  * ### failing_predicate
    ```
    .get_entity.failing_predicate
    ```
  * ### find
    ```
    .get_entity.find
    ```
  * ### from_position
    ```
    .get_entity.from_position
    ```
  * ### in_radius
    ```
    .get_entity.in_radius
    ```
  * ### in_team
    ```
    .get_entity.in_team
    ```
  * ### in_volume
    ```
    .get_entity.in_volume
    ```
  * ### matching_nbt
    ```
    .get_entity.matching_nbt
    ```
  * ### not_in_team
    ```
    .get_entity.not_in_team
    ```
  * ### not_matching_nbt
    ```
    .get_entity.not_matching_nbt
    ```
  * ### of_name
    ```
    .get_entity.of_name
    ```
  * ### of_type
    ```
    .get_entity.of_type
    ```
  * ### passing_predicate
    ```
    .get_entity.passing_predicate
    ```
  * ### with_hrz_rot
    ```
    .get_entity.with_hrz_rot
    ```
  * ### with_no_team
    ```
    .get_entity.with_no_team
    ```
  * ### with_score
    ```
    .get_entity.with_score
    ```
  * ### with_tag
    ```
    .get_entity.with_tag
    ```
  * ### with_vert_rot
    ```
    .get_entity.with_vert_rot
    ```
  * ### without_tag
    ```
    .get_entity.without_tag
    ```
* ### get_player
  ```
  .get_player
  ```
  * ### advancement_matches
    ```
    .get_player.advancement_matches
    ```
  * ### failing_predicate
    ```
    .get_player.failing_predicate
    ```
  * ### find
    ```
    .get_player.find
    ```
  * ### from_position
    ```
    .get_player.from_position
    ```
  * ### in_gamemode
    ```
    .get_player.in_gamemode
    ```
  * ### in_radius
    ```
    .get_player.in_radius
    ```
  * ### in_team
    ```
    .get_player.in_team
    ```
  * ### in_volume
    ```
    .get_player.in_volume
    ```
  * ### matching_nbt
    ```
    .get_player.matching_nbt
    ```
  * ### not_in_gamemode
    ```
    .get_player.not_in_gamemode
    ```
  * ### not_in_team
    ```
    .get_player.not_in_team
    ```
  * ### not_matching_nbt
    ```
    .get_player.not_matching_nbt
    ```
  * ### of_name
    ```
    .get_player.of_name
    ```
  * ### passing_predicate
    ```
    .get_player.passing_predicate
    ```
  * ### with_hrz_rot
    ```
    .get_player.with_hrz_rot
    ```
  * ### with_level
    ```
    .get_player.with_level
    ```
  * ### with_no_team
    ```
    .get_player.with_no_team
    ```
  * ### with_score
    ```
    .get_player.with_score
    ```
  * ### with_tag
    ```
    .get_player.with_tag
    ```
  * ### with_vert_rot
    ```
    .get_player.with_vert_rot
    ```
  * ### without_tag
    ```
    .get_player.without_tag
    ```
* ### get_players
  ```
  .get_players
  ```
  * ### advancement_matches
    ```
    .get_players.advancement_matches
    ```
  * ### failing_predicate
    ```
    .get_players.failing_predicate
    ```
  * ### find
    ```
    .get_players.find
    ```
  * ### from_position
    ```
    .get_players.from_position
    ```
  * ### in_gamemode
    ```
    .get_players.in_gamemode
    ```
  * ### in_radius
    ```
    .get_players.in_radius
    ```
  * ### in_team
    ```
    .get_players.in_team
    ```
  * ### in_volume
    ```
    .get_players.in_volume
    ```
  * ### matching_nbt
    ```
    .get_players.matching_nbt
    ```
  * ### not_in_gamemode
    ```
    .get_players.not_in_gamemode
    ```
  * ### not_in_team
    ```
    .get_players.not_in_team
    ```
  * ### not_matching_nbt
    ```
    .get_players.not_matching_nbt
    ```
  * ### of_name
    ```
    .get_players.of_name
    ```
  * ### passing_predicate
    ```
    .get_players.passing_predicate
    ```
  * ### with_hrz_rot
    ```
    .get_players.with_hrz_rot
    ```
  * ### with_level
    ```
    .get_players.with_level
    ```
  * ### with_no_team
    ```
    .get_players.with_no_team
    ```
  * ### with_score
    ```
    .get_players.with_score
    ```
  * ### with_tag
    ```
    .get_players.with_tag
    ```
  * ### with_vert_rot
    ```
    .get_players.with_vert_rot
    ```
  * ### without_tag
    ```
    .get_players.without_tag
    ```
* ### meta
  ```
  .meta
  ```
  * ### compile_time
    ```
    .meta.compile_time
    ```
* ### pos
  ```
  .pos
  ```
  * ### constant
    ```
    .pos.constant
    ```
  * ### get
    ```
    .pos.get
    ```
  * ### get_directed
    ```
    .pos.get_directed
    ```
  * ### set_coord
    ```
    .pos.set_coord
    ```
* ### rotate
  ```
  .rotate
  ```
  * ### face
    ```
    .rotate.face
    ```
  * ### match
    ```
    .rotate.match
    ```
  * ### set
    ```
    .rotate.set
    ```
* ### scoreboard
  ```
  .scoreboard
  ```
  * ### add_obj
    ```
    .scoreboard.add_obj
    ```
  * ### conf
    ```
    .scoreboard.conf
    ```
    * ### display
      ```
      .scoreboard.conf.display
      ```
      * ### below_name
        ```
        .scoreboard.conf.display.below_name
        ```
      * ### list
        ```
        .scoreboard.conf.display.list
        ```
      * ### sidebar
        ```
        .scoreboard.conf.display.sidebar
        ```
    * ### hearts
      ```
      .scoreboard.conf.hearts
      ```
    * ### json_name
      ```
      .scoreboard.conf.json_name
      ```
  * ### obj
    ```
    .scoreboard.obj
    ```
    * ### add
      ```
      .scoreboard.obj.add
      ```
    * ### enable
      ```
      .scoreboard.obj.enable
      ```
    * ### get
      ```
      .scoreboard.obj.get
      ```
    * ### player
      ```
      .scoreboard.obj.player
      ```
      * ### add
        ```
        .scoreboard.obj.player.add
        ```
      * ### get
        ```
        .scoreboard.obj.player.get
        ```
      * ### reset
        ```
        .scoreboard.obj.player.reset
        ```
      * ### set
        ```
        .scoreboard.obj.player.set
        ```
      * ### sub
        ```
        .scoreboard.obj.player.sub
        ```
    * ### reset
      ```
      .scoreboard.obj.reset
      ```
    * ### set
      ```
      .scoreboard.obj.set
      ```
    * ### sub
      ```
      .scoreboard.obj.sub
      ```
  * ### remove_obj
    ```
    .scoreboard.remove_obj
    ```
  * ### reset
    ```
    .scoreboard.reset
    ```
## Structs
* `std::Color`
* `std::Pos`
