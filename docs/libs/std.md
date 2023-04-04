# std
## Functions
### kill
```
kill() -> null
```
### summon
```
summon(location: std::Pos, entity_type: str!, nbt_data: str!? = null) -> Entity
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
effect_add(effect: str!, seconds: int!, amplifier: int!, particles: bool! = True) -> null
```
### effect_clear
```
effect_clear(effect: str!? = null) -> null
```
### setblock
```
setblock(location: std::Pos, block: str!, mine_existing: bool! = False, keep_existing: bool! = False) -> null
```
### fill
```
fill(pos1: std::Pos, pos2: std::Pos, block: str!, mine_existing: bool! = False, keep_existing: bool! = False) -> null
```
### area_replace
```
area_replace(pos1: std::Pos, pos2: std::Pos, old_block: str!, new_block: str!) -> null
```
### give
```
give(item: str!, count: int!, data: str! = {}) -> null
```
### particle
```
particle(location: std::Pos, particle: str!, dx: float!, dy: float!, dz: float!, speed: float!, count: int!, force_render: bool! = False) -> null
```
### play_sound
```
play_sound(sound_location: std::Pos, sound: str!, channel: str! = master, volume: float! = 1.0, pitch: float! = 1.0, min_volume: float! = 0.0) -> null
```
### print
```
print() -> null
```
### say
```
say(msg: str!) -> null
```
### spread
```
spread(center: std::Pos, radius: float!, spacing: float! = 0.0, respect_teams: bool! = False, max_height: int!? = null) -> null
```
### tag_add
```
tag_add(new_tag: str!) -> null
```
### tag_remove
```
tag_remove(target_tag: str!) -> null
```
### tag_count
```
tag_count() -> int
```
### tp
```
tp(target_location: std::Pos) -> null
```
