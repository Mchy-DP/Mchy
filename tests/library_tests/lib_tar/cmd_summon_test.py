from typing import Optional

import pytest
from mchy.errors import ConversionError, VirtualRepError

from mchy.library.std.cmd_summon import SmtSummonCmd


@pytest.mark.parametrize("tag, nbt, expected", [
    # Pretty empty tests - no tag
    ('fr"ed', r'''''', None),  # invalid tag
    ("fred", r'''''', r'''{Tags:["fred"]}'''),
    ("greg", r'''''', r'''{Tags:["greg"]}'''),
    ("fred", r'''damage:0''', r'''{damage:0,Tags:["fred"]}'''),
    ("fred", r'''damage:0, name:"yob"''', r'''{damage:0, name:"yob",Tags:["fred"]}'''),
    ("fred", r'''damage:0, name:"yob\""''', r'''{damage:0, name:"yob\"",Tags:["fred"]}'''),
    ("fred", r'''damage:0, name:"yo(b"''', r'''{damage:0, name:"yo(b",Tags:["fred"]}'''),
    # Force main parse tests - no tag
    ("fred", r'''cons:"Tags:["''', r'''{cons:"Tags:[",Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", damage:0''', r'''{cons:"Tags:[", damage:0,Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", damage:0, name:"yob"''', r'''{cons:"Tags:[", damage:0, name:"yob",Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", damage:0, name:"yob\""''', r'''{cons:"Tags:[", damage:0, name:"yob\"",Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", damage:0, name:"yo(b"''', r'''{cons:"Tags:[", damage:0, name:"yo(b",Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:[]''', r'''{cons:"Tags:[", data:[],Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:[1,2,3]''', r'''{cons:"Tags:[", data:[1,2,3],Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:{old: "pig"}''', r'''{cons:"Tags:[", data:{old: "pig"},Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:[{a:1b, b:0b}]''', r'''{cons:"Tags:[", data:[{a:1b, b:0b}],Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:[{a:1b, b:0b}, {a:0b, b:1b}]''', r'''{cons:"Tags:[", data:[{a:1b, b:0b}, {a:0b, b:1b}],Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:[{a:1b, b:0b}, {a:0b, b:"Toddle"}]''', r'''{cons:"Tags:[", data:[{a:1b, b:0b}, {a:0b, b:"Toddle"}],Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:[{a:1b, b:0b}, {a:0b, b:"Tod,dle"}]''', r'''{cons:"Tags:[", data:[{a:1b, b:0b}, {a:0b, b:"Tod,dle"}],Tags:["fred"]}'''),
    ("fred", r'''cons:"Tags:[", b:[{a:[]}]''', r'''{cons:"Tags:[", b:[{a:[]}],Tags:["fred"]}'''),
    # Malformed nbt tests
    ("fred", r'''cons:"Tags:[", b:''', None),
    ("fred", r'''cons:"Tags:[", b:[''', None),
    ("fred", r'''cons:"Tags:[", b:]''', None),
    ("fred", r'''cons:"Tags:[", b:"''', None),
    ("fred", r'''cons:"Tags:[", b:[{a:[}]''', None),
    ("fred", r'''cons:"Tags:[", b:[{a:"}]''', None),
    # Tags tests
    ("fred", r'''Tags:[]''', r'''{Tags:["fred"]}'''),
    ("fred", r'''Tags:[ ]''', r'''{Tags:["fred"]}'''),
    ("fred", r'''Tags:["greg"]''', r'''{Tags:["greg","fred"]}'''),
    ("fred", r'''Tags:["greg",]''', r'''{Tags:["greg","fred"]}'''),
    ("fred", r''' Tags:["greg"]''', r'''{ Tags:["greg","fred"]}'''),
    ("fred", r'''Tags:["greg","steve"]''', r'''{Tags:["greg","steve","fred"]}'''),
    ("fred", r'''cons:"Tags:[", data:[{a:1b, b:0b}], Tags:["greg","steve"]''', r'''{cons:"Tags:[", data:[{a:1b, b:0b}], Tags:["greg","steve","fred"]}'''),
    ("fred", r'''Tags:["greg"], damage:0''', r'''{Tags:["greg","fred"], damage:0}'''),
    ("fred", r'''break: 42, Tags:["greg"], damage:0''', r'''{break: 42, Tags:["greg","fred"], damage:0}'''),
    ("fred", r'''TAgs: 42, Tags:["greg"]''', r'''{TAgs: 42, Tags:["greg","fred"]}'''),
    ("fred", r'''Tags2: 42, Tags:["greg"]''', r'''{Tags2: 42, Tags:["greg","fred"]}'''),
    # Realish nightmare tag:
    ("Active", (
            r'''Fire:31,CustomNameVisible:1b,Tags:["Fireball"],CustomName:'{"text":"}}})9(),£1dawdINCONVIENT\'{}(}}{{}({)(}\\""}',HandItems:''' +
            r'''[{id:"minecraft:mud",Count:2b,tag:{CanDestroy:["minecraft:ice"]}},{}],Attributes:[{Name:generic.attack_damage,Base:123}]'''
        ), (
            r'''{Fire:31,CustomNameVisible:1b,Tags:["Fireball","Active"],CustomName:'{"text":"}}})9(),£1dawdINCONVIENT\'{}(}}{{}({)(}\\""}',HandItems:''' +
            r'''[{id:"minecraft:mud",Count:2b,tag:{CanDestroy:["minecraft:ice"]}},{}],Attributes:[{Name:generic.attack_damage,Base:123}]}'''
        ))
])
def test_tag_insert_parsing_good(tag: str, nbt: str, expected: Optional[str]):
    if expected is None:
        with pytest.raises((VirtualRepError, ConversionError)):
            SmtSummonCmd.parse_nbt_data(nbt, tag)
    else:
        assert SmtSummonCmd.parse_nbt_data(nbt, tag) == expected
