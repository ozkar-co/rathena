# Garrett v2 proposal

Seed: `20261118`. Fixed table, no dynamic generation.

## Summary

```json
{
  "offers": 200,
  "missions": 50,
  "missionsByTier": {
    "common": 20,
    "uncommon": 20,
    "rare": 10
  },
  "missionPayoutAvg": 1018340,
  "missionPayoutMin": 715000,
  "missionPayoutMax": 1408000,
  "missionQtyMin": 5,
  "missionQtyMax": 500,
  "missionRatioAvg": 1.259,
  "weightLimited": 26
}
```

## Missions

| # | Tier | Item | Qty | Canonical buy | Garrett unit | Payout | Buy value | Mob | HP | Mob lvl | Abundance | Difficulty | Partial | Forfeit |
|---:|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|---|---|---|
| 1 | common | Lantern | 500 | 1,300 | 1,500 | 825,000 | 650,000 | Skeleton Worker | 2,302 | 44 | abundant | easy | yes | yes |
| 2 | common | Bug Leg | 500 | 1,300 | 1,500 | 825,000 | 650,000 | Argiope | 7,140 | 75 | abundant | easy | yes | yes |
| 3 | common | Acorn | 500 | 1,200 | 1,400 | 770,000 | 600,000 | Coco | 1,388 | 38 | abundant | easy | yes | yes |
| 4 | common | Stone | 166 | 3,600 | 4,100 | 749,000 | 597,600 | Shellfish | 2,652 | 50 | abundant | easy | yes | yes |
| 5 | common | Heart of Mermaid | 500 | 1,400 | 1,600 | 880,000 | 700,000 | Iara | 8,524 | 79 | abundant | easy | yes | yes |
| 6 | common | Blue Hair | 500 | 1,400 | 1,600 | 880,000 | 700,000 | Kobold Archer | 22,944 | 108 | abundant | easy | yes | yes |
| 7 | common | Inside-out Shirt | 157 | 4,400 | 5,100 | 881,000 | 690,800 | Wakwak | 35,738 | 111 | abundant | easy | yes | yes |
| 8 | common | Fine Grit | 401 | 1,700 | 2,000 | 882,000 | 681,700 | Scorpion | 272 | 16 | abundant | easy | yes | yes |
| 9 | common | Oil Paper | 334 | 2,100 | 2,400 | 882,000 | 701,400 | Karakasa | 6,054 | 72 | abundant | easy | yes | yes |
| 10 | common | Rotten Bandage | 500 | 1,100 | 1,300 | 715,000 | 550,000 | Zombie Prisoner | 13,804 | 89 | abundant | easy | yes | yes |
| 11 | common | Bear's Footskin | 500 | 1,100 | 1,300 | 715,000 | 550,000 | Bigfoot | 1,012 | 29 | abundant | easy | yes | yes |
| 12 | common | Sea-Otter Fur | 500 | 1,100 | 1,300 | 715,000 | 550,000 | Sea Otter | 2,948 | 48 | abundant | easy | yes | yes |
| 13 | common | Slingshot | 500 | 1,100 | 1,300 | 715,000 | 550,000 | Wootan Shooter | 5,236 | 67 | abundant | easy | yes | yes |
| 14 | common | Cotton Shirt | 50 | 14,000 | 16,100 | 886,000 | 700,000 | Picky | 140 | 9 | abundant | easy | yes | yes |
| 15 | common | Clam Flesh | 145 | 4,900 | 5,600 | 893,000 | 710,500 | Red Eruma | 16,058 | 91 | abundant | easy | yes | yes |
| 16 | common | Solid Trunk | 451 | 1,600 | 1,800 | 893,000 | 721,600 | Willow | 156 | 8 | abundant | easy | yes | yes |
| 17 | common | Elegant Flower | 94 | 7,600 | 8,700 | 900,000 | 714,400 | Mangkukulam | 29,114 | 110 | abundant | easy | yes | yes |
| 18 | common | Rainbow Shell | 356 | 2,000 | 2,300 | 901,000 | 712,000 | Stainer | 424 | 21 | abundant | easy | yes | yes |
| 19 | common | Barren Trunk | 456 | 1,600 | 1,800 | 903,000 | 729,600 | Willow | 156 | 8 | abundant | easy | yes | yes |
| 20 | common | Mysterious Flower | 152 | 4,700 | 5,400 | 903,000 | 714,400 | Tiyanak | 23,178 | 105 | abundant | easy | yes | yes |
| 21 | uncommon | Singing Flower | 100 | 8,200 | 9,400 | 1,034,000 | 820,000 | Mavka | 9,980 | 84 | common | easy | yes | yes |
| 22 | uncommon | Deadly Noxious Herb | 100 | 8,600 | 9,900 | 1,089,000 | 860,000 | Marina | 2,020 | 42 | common | easy | yes | yes |
| 23 | uncommon | Pet Incubator | 166 | 5,200 | 6,000 | 1,096,000 | 863,200 | Eggyra | 2,472 | 53 | common | easy | yes | yes |
| 24 | uncommon | Bitter Herb | 100 | 7,900 | 9,100 | 1,001,000 | 790,000 | Kikimora | 11,090 | 85 | common | easy | yes | yes |
| 25 | uncommon | Crystal Mirror | 100 | 7,900 | 9,100 | 1,001,000 | 790,000 | Mavka | 9,980 | 84 | common | easy | yes | yes |
| 26 | uncommon | Diamond Ring | 50 | 23,600 | 20,100 | 1,106,000 | 1,180,000 | Succubus | 50,594 | 119 | common | easy | yes | yes |
| 27 | uncommon | Blue Bijou | 500 | 1,600 | 1,800 | 990,000 | 800,000 | Acidus | 78,178 | 130 | common | medium | yes | yes |
| 28 | uncommon | Yggdrasil Dust | 500 | 1,600 | 1,800 | 990,000 | 800,000 | Cenere | 260,262 | 146 | common | medium | yes | yes |
| 29 | uncommon | Old Magicbook | 166 | 4,700 | 5,400 | 986,000 | 780,200 | Rideword | 5,710 | 74 | common | medium | yes | yes |
| 30 | uncommon | Rotten Meat | 18 | 50,000 | 57,500 | 1,138,000 | 900,000 | Roween | 13,234 | 95 | abundant | medium | yes | yes |
| 31 | uncommon | Orange Juice | 100 | 9,000 | 10,400 | 1,144,000 | 900,000 | Drops | 92 | 2 | common | easy | yes | yes |
| 32 | uncommon | Ment | 54 | 16,900 | 19,400 | 1,152,000 | 912,600 | Rafflesia | 9,884 | 86 | common | easy | yes | yes |
| 33 | uncommon | Rusty Iron | 100 | 7,500 | 8,600 | 946,000 | 750,000 | Scorpion | 272 | 16 | common | easy | yes | yes |
| 34 | uncommon | Claw of Desert Wolf | 500 | 1,800 | 2,100 | 1,155,000 | 900,000 | Desert Wolf | 20,488 | 103 | abundant | medium | yes | yes |
| 35 | uncommon | Yellow Bijou | 500 | 1,800 | 2,100 | 1,155,000 | 900,000 | Acidus | 81,900 | 130 | common | medium | yes | yes |
| 36 | uncommon | Burnt Part | 309 | 3,000 | 3,400 | 1,156,000 | 927,000 | Alicel | 36,638 | 115 | abundant | medium | yes | yes |
| 37 | uncommon | Hinalle | 224 | 4,100 | 4,700 | 1,158,000 | 918,400 | Rocker | 310 | 15 | common | easy | yes | yes |
| 38 | uncommon | Munak Doll | 65 | 14,100 | 16,200 | 1,158,000 | 916,500 | Yao Jun | 12,826 | 87 | common | easy | yes | yes |
| 39 | uncommon | Tongue | 500 | 1,500 | 1,700 | 935,000 | 750,000 | Rybio | 19,878 | 98 | abundant | medium | yes | yes |
| 40 | uncommon | Gas Mask | 50 | 14,700 | 16,900 | 930,000 | 735,000 | Remover | 66,204 | 121 | common | medium | yes | yes |
| 41 | rare | Galapago Card | 200 | 5,000 | 5,800 | 1,276,000 | 1,000,000 | Galapago | 1,964 | 45 | scarce | easy | yes | yes |
| 42 | rare | Lava Leather Manteau | 12 | 88,100 | 101,000 | 1,333,000 | 1,057,200 | Rigid Nightmare Terror | 2,437,404 | 179 | common | hard | yes | yes |
| 43 | rare | Ant Jaw | 200 | 4,900 | 5,600 | 1,232,000 | 980,000 | Jewelry Ant | 4,891,312 | 191 | common | extreme | yes | yes |
| 44 | rare | Skeleton Prisoner Card | 200 | 4,900 | 5,600 | 1,232,000 | 980,000 | Skeleton Prisoner | 16,756 | 91 | rare | easy | yes | yes |
| 45 | rare | Girl's Diary | 16 | 67,800 | 78,000 | 1,373,000 | 1,084,800 | Munak | 4,004 | 58 | uncommon | easy | yes | yes |
| 46 | rare | Old Portrait | 50 | 19,400 | 22,300 | 1,226,000 | 970,000 | Bongun | 4,130 | 59 | uncommon | easy | yes | yes |
| 47 | rare | Comodo Card | 200 | 4,800 | 5,500 | 1,210,000 | 960,000 | Comodo | 8,582 | 81 | uncommon | easy | yes | yes |
| 48 | rare | Luxury Doram Manteau | 12 | 92,000 | 106,000 | 1,399,000 | 1,104,000 | Rake Scaraba | 135,400 | 139 | common | hard | yes | yes |
| 49 | rare | Green Whistle | 6 | 157,000 | 181,000 | 1,195,000 | 942,000 | Alphoccio | 512,404 | 142 | common | hard | yes | yes |
| 50 | rare | Goblin Leader Card | 5 | 223,000 | 256,000 | 1,408,000 | 1,115,000 | Goblin Leader | 43,384 | 55 | rare | easy | yes | yes |

## Offers

| # | Item | Canonical buy | Garrett buy | Mid | Abundance | Demand | Mob | HP | Mob lvl | Map | Spawn | Drop |
|---:|---|---:|---:|---:|---|---|---|---:|---:|---|---:|---:|
| 1 | Nose Ring | 441 | 507 | 736 | abundant | unknown | Majoruros | 27,044 | 107 | gl_dun02 | 52 | 2207 |
| 2 | Solid Iron Piece | 443 | 509 | 1,200 | abundant | none | Alicel | 36,638 | 115 | kh_dun02 | 41 | 1500 |
| 3 | White Herb | 448 | 507 | 597 | abundant | high | Stem Worm | 8,168 | 84 | lhz_fild02 | 100 | 900 |
| 4 | Wolf Claw | 451 | 519 | 1,200 | abundant | low | Wolf | 2,182 | 45 | moc_fild03 | 164 | 4500 |
| 5 | Nipper | 474 | 545 | 790 | abundant | none | Vadon | 2,182 | 45 | iz_dun01 | 60 | 4500 |
| 6 | Clover | 487 | 560 | 811 | abundant | medium | Lunatic | 96 | 3 | prt_fild01 | 196 | 7000 |
| 7 | Monster Blood | 488 | 561 | 814 | abundant | none | Fire Sandman | 261,002 | 143 | moro_vol | 30 | 1500 |
| 8 | Rusty Screw | 507 | 575 | 676 | abundant | high | Teddy Bear | 12,568 | 91 | ein_fild03 | 100 | 1900 |
| 9 | Bow | 525 | 604 | 950 | abundant | medium | Condor | 210 | 12 | moc_fild11 | 137 | 100 |
| 10 | Well-baked Cookie | 528 | 607 | 1,200 | abundant | unknown | Christmas Cookie | 1,322 | 37 | xmas_dun01 | 49 | 2000 |
| 11 | Honey | 529 | 608 | 1,500 | abundant | high | Teddy Bear | 12,568 | 91 | ein_fild03 | 100 | 500 |
| 12 | Delicious Jelly | 544 | 626 | 1,200 | abundant | unknown | Siorava | 11,154 | 87 | mal_dun01 | 45 | 700 |
| 13 | Venom Canine | 549 | 622 | 732 | abundant | high | Anacondaq | 18,466 | 100 | ra_fild08 | 159 | 4500 |
| 14 | Glass Bead | 551 | 634 | 998 | abundant | none | Sea Otter | 2,948 | 48 | cmd_fild04 | 149 | 325 |
| 15 | Yam | 558 | 642 | 1,200 | abundant | unknown | Grizzly | 4,370 | 66 | lou_dun01 | 17 | 1250 |
| 16 | Rice Cake | 566 | 651 | 1,300 | abundant | unknown | Taoist Hermit | 19,454 | 96 | gon_dun03 | 40 | 2250 |
| 17 | Emveretarcon | 570 | 656 | 950 | abundant | medium | Mineral | 15,918 | 96 | ein_dun02 | 50 | 400 |
| 18 | Harpy Feather | 600 | 510 | 600 | abundant | none | Harpy | 8,908 | 83 | yuno_fild03 | 174 | 2425 |
| 19 | Green Herb | 612 | 694 | 816 | abundant | high | Fabre | 118 | 6 | prt_fild06 | 149 | 3000 |
| 20 | Concentration Potion | 630 | 536 | 630 | abundant | medium | Raggler | 1,970 | 48 | cmd_fild07 | 116 | 100 |
| 21 | Short Daenggie | 646 | 743 | 1,700 | abundant | none | Bongun | 4,130 | 59 | pay_dun02 | 30 | 2750 |
| 22 | Worn-out Prison Uniform | 654 | 752 | 1,700 | abundant | none | Alligator | 3,878 | 57 | cmd_fild03 | 194 | 300 |
| 23 | Dark Crystal Fragment | 670 | 770 | 1,900 | abundant | low | Obsidian | 16,984 | 97 | ein_dun02 | 40 | 1500 |
| 24 | Blue Herb | 676 | 766 | 901 | abundant | high | Goat | 5,810 | 80 | yuno_fild11 | 139 | 500 |
| 25 | Log | 676 | 777 | 1,800 | abundant | medium | Stone Shooter | 3,680 | 64 | um_fild01 | 40 | 2500 |
| 26 | Scorpion Tail | 697 | 802 | 1,200 | abundant | high | Scorpion | 272 | 16 | moc_fild18 | 160 | 2750 |
| 27 | Worm Peeling | 704 | 810 | 1,900 | abundant | low | Andre | 1,074 | 33 | cmd_fild08 | 62 | 4500 |
| 28 | Steel | 712 | 808 | 950 | abundant | high | Pitman | 13,434 | 90 | ein_dun01 | 70 | 250 |
| 29 | Squid Ink | 725 | 834 | 1,200 | abundant | none | Sedora | 33,480 | 110 | iz_dun05 | 60 | 1500 |
| 30 | Grit | 737 | 848 | 1,200 | abundant | none | Sleeper | 9,010 | 81 | yuno_fild02 | 185 | 2668 |
| 31 | Antelope Skin | 751 | 864 | 2,000 | abundant | none | Goat | 5,810 | 80 | yuno_fild11 | 139 | 1250 |
| 32 | Earthworm Peeling | 768 | 883 | 2,200 | abundant | high | Hode | 4,694 | 63 | moc_fild17 | 170 | 4500 |
| 33 | Nine Tails | 774 | 890 | 2,200 | abundant | high | Nine Tail | 4,844 | 72 | pay_dun04 | 30 | 2328 |
| 34 | Flexible Tube | 780 | 897 | 2,200 | abundant | none | Metaling | 7,724 | 81 | ein_fild08 | 139 | 2000 |
| 35 | Oridecon | 784 | 850 | 1,000 | abundant | high | Big Bell | 333,720 | 163 | c_tower3_ | 109 | 100 |
| 36 | Elunium | 784 | 850 | 1,000 | abundant | high | Banaspaty | 6,470 | 85 | dew_dun02 | 70 | 750 |
| 37 | Star Dust | 788 | 906 | 1,400 | abundant | medium | Sandman | 4,648 | 61 | moc_fild16 | 130 | 100 |
| 38 | Trunk | 822 | 945 | 2,300 | abundant | medium | Greatest General | 2,810 | 55 | pay_fild10 | 129 | 1000 |
| 39 | Light Granule | 855 | 983 | 1,400 | abundant | high | Hillthrion | 52,252 | 123 | man_fild03 | 33 | 600 |
| 40 | Coral Reef | 871 | 1,000 | 2,500 | abundant | high | Penomena | 9,242 | 85 | alde_dun03 | 85 | 2425 |
| 41 | Research Chart | 899 | 1,000 | 1,500 | abundant | medium | Gertie | 533,852 | 141 | lhz_dun04 | 57 | 2000 |
| 42 | Horrendous Hair | 915 | 1,000 | 1,200 | abundant | high | Medusa | 22,560 | 102 | beach_dun | 60 | 2668 |
| 43 | Pointed Scale | 979 | 1,100 | 1,600 | abundant | none | Wormtail | 372 | 17 | pay_fild06 | 140 | 2750 |
| 44 | Little Evil Horn | 990 | 1,100 | 1,700 | abundant | low | Deviruchi | 14,330 | 93 | gef_dun02 | 45 | 2668 |
| 45 | Shell | 1,000 | 1,200 | 1,700 | abundant | high | Horn | 1,128 | 32 | pay_fild09 | 181 | 2750 |
| 46 | Decayed Nail | 1,000 | 1,200 | 1,400 | abundant | high | Zombie | 408 | 17 | pay_dun00 | 40 | 9000 |
| 47 | Little Evil Wing | 1,000 | 1,200 | 2,400 | abundant | low | Gargoyle | 18,466 | 100 | gl_sew02 | 89 | 250 |
| 48 | Reins | 1,000 | 1,200 | 2,700 | abundant | none | Abysmal Knight | 69,372 | 122 | gl_knt01 | 14 | 2668 |
| 49 | Professional Cooking Kit | 1,000 | 850 | 1,000 | abundant | unknown | Venatu | 36,184 | 113 | juperos_01 | 70 | 50 |
| 50 | Soft Feather | 1,100 | 1,300 | 1,800 | abundant | high | Cornus | 46,234 | 120 | spl_fild03 | 52 | 1500 |
| 51 | Elder Branch | 1,100 | 1,200 | 1,400 | abundant | high | Dark Pinguicula | 36,184 | 113 | spl_fild01 | 98 | 750 |
| 52 | Candy | 1,200 | 1,400 | 3,100 | abundant | none | Marin | 1,688 | 37 | xmas_fild01 | 65 | 175 |
| 53 | Maneater Root | 1,300 | 1,500 | 2,200 | abundant | high | Rafflesia | 9,884 | 86 | lhz_fild01 | 170 | 2750 |
| 54 | Wand | 1,400 | 1,600 | 2,400 | abundant | medium | Peco Peco | 708 | 25 | moc_fild02 | 153 | 50 |
| 55 | Cheese | 1,500 | 1,300 | 1,500 | abundant | unknown | Taoist Hermit | 19,454 | 96 | gon_dun03 | 40 | 2800 |
| 56 | Javelin | 1,500 | 1,700 | 4,000 | abundant | low | Rocker | 310 | 15 | prt_fild07 | 203 | 80 |
| 57 | Anolian Skin | 1,500 | 1,700 | 2,000 | abundant | high | Anolian | 33,230 | 109 | gl_sew04 | 126 | 2425 |
| 58 | Hinalle Leaflet | 1,600 | 1,800 | 4,500 | abundant | medium | Grove | 3,468 | 55 | cmd_fild01 | 202 | 500 |
| 59 | Piece of Cake | 1,600 | 1,800 | 3,800 | abundant | low | Myst Case | 1,618 | 39 | xmas_dun02 | 70 | 1000 |
| 60 | Warrior's Will | 1,600 | 1,800 | 2,700 | abundant | medium | Cecil Damon | 400,510 | 141 | lhz_dun03 | 81 | 200 |
| 61 | Slick Paper | 1,700 | 2,000 | 2,900 | abundant | none | Karakasa | 6,054 | 72 | ama_fild01 | 72 | 1100 |
| 62 | Grape | 2,000 | 2,300 | 83,200 | abundant | medium | Poporing | 978 | 30 | pay_fild04 | 141 | 200 |
| 63 | Dragon Scale | 2,000 | 2,300 | 3,400 | abundant | high | Petite | 6,394 | 79 | gef_fild08 | 163 | 2668 |
| 64 | Fine Sand | 2,000 | 2,300 | 5,800 | abundant | low | Sleeper | 9,010 | 81 | yuno_fild02 | 185 | 600 |
| 65 | Porcupine Quill | 2,100 | 2,400 | 3,600 | abundant | low | Caramel | 638 | 25 | mjolnir_01 | 167 | 4500 |
| 66 | Yoyo Tail | 2,200 | 2,500 | 3,700 | abundant | low | Yoyo | 1,388 | 38 | prt_fild03 | 127 | 4500 |
| 67 | Snail's Shell | 2,200 | 2,500 | 3,700 | abundant | low | Ambernite | 530 | 19 | prt_fild04 | 111 | 8000 |
| 68 | Mystic Horn | 2,200 | 2,500 | 3,700 | abundant | medium | Cornus | 46,234 | 120 | spl_fild03 | 52 | 4000 |
| 69 | Worn-out Magic Scroll | 2,200 | 2,500 | 3,700 | abundant | medium | Elder | 15,560 | 92 | tha_t04 | 20 | 2000 |
| 70 | Spawn | 2,300 | 2,600 | 3,900 | abundant | low | Comodo | 8,582 | 81 | dew_dun01 | 100 | 2500 |
| 71 | Hat | 525 | 604 | 950 | common | low | Poison Spore | 758 | 26 | mjolnir_06 | 100 | 10 |
| 72 | Adventurer's Suit | 570 | 656 | 950 | common | none | Baby Desert Wolf | 226 | 14 | moc_fild11 | 137 | 40 |
| 73 | Candy Cane | 618 | 711 | 1,800 | common | low | Cookie | 1,194 | 35 | xmas_dun01 | 49 | 75 |
| 74 | Sunflower | 770 | 885 | 2,100 | common | low | Geographer | 6,816 | 73 | yuno_fild01 | 75 | 15 |
| 75 | Falchion | 788 | 906 | 1,400 | common | medium | Pirate Skeleton | 2,702 | 48 | treasure01 | 56 | 125 |
| 76 | Flower Ring | 788 | 670 | 788 | common | unknown | Toucan | 5,128 | 70 | bra_fild01 | 60 | 100 |
| 77 | Mace | 840 | 966 | 1,500 | common | medium | Curupira | 5,122 | 68 | bra_fild01 | 50 | 50 |
| 78 | Egg | 852 | 980 | 1,900 | common | unknown | Leshij | 9,440 | 81 | mosk_dun01 | 74 | 25 |
| 79 | Spear | 892 | 1,000 | 1,600 | common | low | Mandragora | 280 | 13 | gef_fild04 | 125 | 30 |
| 80 | Level 5 Fire Wall | 1,000 | 850 | 1,000 | common | none | Marionette | 8,178 | 90 | gef_dun02 | 30 | 50 |
| 81 | Katana | 1,000 | 1,200 | 1,900 | common | medium | Boa | 406 | 18 | pay_fild02 | 142 | 20 |
| 82 | Singing Plant | 1,100 | 1,300 | 1,800 | common | medium | Mavka | 9,980 | 84 | mosk_dun03 | 17 | 150 |
| 83 | Red Frame | 1,200 | 1,000 | 1,200 | common | unknown | Dark Frame | 7,306 | 76 | gl_cas01 | 35 | 500 |
| 84 | Main Gauche | 1,300 | 1,500 | 2,300 | common | low | Poporing | 978 | 30 | pay_fild04 | 141 | 20 |
| 85 | Main Gauche | 1,300 | 1,500 | 2,300 | common | high | Hornet | 170 | 11 | prt_fild05 | 199 | 20 |
| 86 | Wand | 1,300 | 1,500 | 2,400 | common | unknown | Goblin | 3,754 | 56 | prt_fild11 | 60 | 8 |
| 87 | Composite Bow | 1,300 | 1,500 | 2,400 | common | low | Goblin Archer | 2,974 | 55 | prt_fild11 | 50 | 13 |
| 88 | Red Bijou | 1,300 | 1,500 | 2,200 | common | low | Ferus | 69,764 | 126 | abyss_02 | 50 | 400 |
| 89 | Green Lace | 1,300 | 1,500 | 2,100 | common | medium | Wormtail | 372 | 17 | pay_fild06 | 140 | 50 |
| 90 | White Powder | 1,400 | 1,600 | 3,600 | common | none | Anacondaq | 18,466 | 100 | ra_fild08 | 159 | 100 |
| 91 | Cat's Eye | 1,400 | 1,600 | 3,900 | common | none | Mao Guai | 10,930 | 89 | lou_dun03 | 18 | 1000 |
| 92 | Green Bijou | 1,400 | 1,600 | 2,400 | common | low | Ferus | 84,448 | 126 | abyss_01 | 55 | 400 |
| 93 | Chivalry Emblem | 1,500 | 1,700 | 3,900 | common | medium | Raydric | 43,962 | 115 | gl_knt01 | 126 | 5 |
| 94 | Anodyne | 1,600 | 1,800 | 2,100 | common | medium | Noxious | 8,924 | 87 | ein_fild05 | 100 | 25 |
| 95 | Chonchon Doll | 1,600 | 1,800 | 2,400 | common | unknown | Chonchon | 96 | 5 | gef_fild00 | 160 | 6 |
| 96 | Peridot | 1,600 | 1,800 | 2,800 | common | unknown | Jewelry Ant | 4,891,312 | 191 | ein_dun03 | 20 | 750 |
| 97 | Pike | 1,800 | 2,100 | 3,300 | common | medium | Wormtail | 372 | 17 | pay_fild06 | 140 | 15 |
| 98 | Shoes | 1,800 | 2,100 | 3,300 | common | medium | Munak | 4,004 | 58 | pay_dun02 | 40 | 8 |
| 99 | Banana Juice | 2,000 | 2,300 | 101,000 | common | medium | Choco | 1,970 | 48 | um_fild02 | 8 | 500 |
| 100 | Emerald | 2,400 | 2,000 | 2,400 | common | none | Roda Frog | 280 | 13 | prt_fild00 | 169 | 8 |
| 101 | Sapphire | 2,400 | 2,000 | 2,400 | common | none | Sea Otter | 2,948 | 48 | cmd_fild04 | 149 | 25 |
| 102 | Bizarre Stone Carvings | 2,400 | 2,800 | 3,900 | common | none | Green Mineral | 4,871,404 | 190 | ein_dun03 | 40 | 150 |
| 103 | Blue Potion | 2,700 | 3,100 | 3,600 | common | high | Dark Priest | 21,686 | 98 | gl_chyard | 95 | 50 |
| 104 | Yggdrasil Berry | 2,800 | 3,200 | 4,800 | common | high | Combat Basilisk | 432,072 | 148 | lasa_dun03 | 110 | 80 |
| 105 | Battle Axe | 2,800 | 3,200 | 5,100 | common | low | Orc Warrior | 2,094 | 44 | gef_fild10 | 179 | 5 |
| 106 | Amethyst | 3,200 | 2,700 | 3,200 | common | high | Argiope | 7,140 | 75 | mjolnir_11 | 170 | 5 |
| 107 | Pearl | 3,200 | 3,700 | 5,700 | common | medium | Sea Otter | 2,948 | 48 | cmd_fild04 | 149 | 75 |
| 108 | Sardonyx | 3,200 | 2,700 | 3,200 | common | none | Drainliar | 2,364 | 47 | alde_dun03 | 55 | 10 |
| 109 | Opal | 3,200 | 2,700 | 3,200 | common | low | Zombie | 408 | 17 | pay_dun00 | 40 | 70 |
| 110 | Topaz | 3,200 | 3,700 | 4,300 | common | medium | Mineral | 15,918 | 96 | ein_dun02 | 50 | 250 |
| 111 | Aquamarine | 3,400 | 3,900 | 5,700 | common | high | Merman | 4,648 | 60 | iz_dun04 | 61 | 20 |
| 112 | Yggdrasil Seed | 3,600 | 4,100 | 4,800 | common | high | Stem Worm | 8,168 | 84 | lhz_fild02 | 100 | 5 |
| 113 | Claw of Monkey | 3,600 | 4,100 | 8,100 | common | unknown | Choco | 1,970 | 48 | um_fild02 | 8 | 2668 |
| 114 | Silver Robe | 3,700 | 4,300 | 5,900 | common | low | Laurell Weinder | 80,564 | 133 | lhz_dun02 | 50 | 15 |
| 115 | 1carat Diamond | 3,900 | 4,500 | 7,100 | common | none | Obsidian | 16,984 | 97 | ein_dun02 | 40 | 250 |
| 116 | Coconut Fruit | 3,900 | 4,500 | 8,600 | common | unknown | Galapago | 1,964 | 45 | cmd_fild02 | 40 | 150 |
| 117 | Folding Fan of Cat Ghost | 3,900 | 4,500 | 8,700 | common | unknown | Mao Guai | 10,930 | 89 | lou_dun03 | 18 | 2086 |
| 118 | Little Ghost Doll | 3,900 | 4,500 | 8,600 | common | unknown | Zhu Po Long | 8,308 | 82 | lou_dun03 | 30 | 400 |
| 119 | Red Chile | 3,900 | 4,500 | 8,700 | common | unknown | Kraben | 4,318 | 70 | ayo_dun02 | 23 | 500 |
| 120 | Gift Box | 4,000 | 4,500 | 5,300 | common | high | Ancient Mimic | 39,556 | 112 | tha_t02 | 80 | 25 |
| 121 | Old Manteau | 4,000 | 4,600 | 8,900 | common | unknown | Bloody Murderer | 34,934 | 110 | nif_fild02 | 11 | 2086 |
| 122 | Crest Piece | 4,000 | 4,600 | 9,000 | common | unknown | Venatu | 36,184 | 113 | juperos_01 | 70 | 175 |
| 123 | White Mask | 4,000 | 4,600 | 9,000 | common | unknown | Aunoe | 29,114 | 110 | arug_dun01 | 22 | 1250 |
| 124 | Crest Piece | 4,100 | 4,700 | 9,000 | common | unknown | Venatu | 37,992 | 113 | juperos_01 | 70 | 200 |
| 125 | Spore Doll | 4,200 | 4,800 | 11,100 | common | none | Spore | 446 | 18 | pay_fild08 | 148 | 10 |
| 126 | Silk Robe | 4,200 | 4,800 | 7,600 | common | high | Creamy | 494 | 23 | gef_fild05 | 143 | 20 |
| 127 | Oil Bottle | 4,200 | 4,800 | 9,200 | common | unknown | Venatu | 36,184 | 113 | juperos_01 | 70 | 50 |
| 128 | Savage Meat | 4,200 | 4,800 | 11,300 | common | medium | Savage | 4,316 | 59 | mjolnir_07 | 161 | 25 |
| 129 | Old Shuriken | 4,200 | 4,800 | 9,400 | common | unknown | Assaulter | 17,544 | 100 | tur_dun04 | 42 | 420 |
| 130 | Frilldora's Fiery Nape | 4,400 | 5,100 | 9,700 | common | unknown | Fire Frilldora | 282,602 | 147 | moro_vol | 30 | 1500 |
| 131 | Battered Kettle | 4,400 | 5,100 | 9,700 | common | unknown | Old Stove | 15,560 | 92 | ein_dun02 | 30 | 500 |
| 132 | Crest Piece | 4,400 | 5,100 | 9,700 | common | unknown | Venatu | 41,610 | 113 | juperos_01 | 50 | 150 |
| 133 | Crystalized Teardrop | 4,500 | 5,200 | 10,100 | common | unknown | Aqua Elemental | 74,840 | 121 | nyd_dun01 | 20 | 500 |
| 134 | Stone Of Blessing | 4,500 | 5,200 | 10,100 | common | unknown | Fire Golem | 360,426 | 148 | moro_vol | 30 | 2000 |
| 135 | Golem's Fiery Stone Tooth | 4,500 | 5,200 | 10,100 | common | unknown | Fire Golem | 360,426 | 148 | moro_vol | 30 | 1500 |
| 136 | Insect Leg | 4,600 | 5,300 | 10,300 | common | unknown | Jewelry Ant | 4,891,312 | 191 | ein_dun03 | 20 | 2250 |
| 137 | Biretta | 4,700 | 5,400 | 8,600 | common | low | Evil Druid | 9,440 | 80 | gl_church | 85 | 5 |
| 138 | Nursing Bottle | 4,800 | 5,500 | 10,700 | common | unknown | Orc Baby | 1,808 | 43 | gef_fild10 | 27 | 100 |
| 139 | Scorpion Claw | 4,900 | 5,600 | 10,900 | common | unknown | Gig | 13,852 | 100 | mag_dun02 | 10 | 1000 |
| 140 | Evil Horn | 5,100 | 5,900 | 11,300 | common | unknown | Baphomet Jr. | 3,526 | 57 | prt_maze03 | 25 | 250 |
| 141 | Branch | 1,600 | 1,800 | 2,800 | uncommon | unknown | Cruiser | 1,842 | 41 | xmas_dun02 | 49 | 3 |
| 142 | Marin Card | 2,100 | 2,400 | 5,500 | uncommon | low | Marin | 1,688 | 37 | xmas_fild01 | 65 | 1 |
| 143 | Fragment of Darkness | 2,300 | 2,600 | 6,200 | uncommon | low | Furious Incarnation of M | 639,000 | 132 | moc_fild22 | 3 | 7500 |
| 144 | Ruby | 2,400 | 2,800 | 4,300 | uncommon | low | Furious Baroness of Retr | 316,630 | 121 | tha_t10 | 2 | 2500 |
| 145 | Muffler | 2,600 | 3,000 | 4,800 | uncommon | medium | Sohee | 5,056 | 64 | pay_dun03 | 70 | 3 |
| 146 | Sweet Roda Frog Card | 2,800 | 3,200 | 7,500 | uncommon | low | Sweet Roda Frog | 280 | 14 | lasa_fild02 | 100 | 10 |
| 147 | Flora Card | 3,400 | 3,900 | 9,200 | uncommon | low | Flora | 4,130 | 59 | cmd_fild01 | 67 | 1 |
| 148 | Scorpion Card | 3,700 | 4,300 | 9,900 | uncommon | low | Scorpion | 272 | 16 | moc_fild18 | 160 | 1 |
| 149 | Seal Card | 3,900 | 4,500 | 10,300 | uncommon | low | Seal | 2,600 | 47 | cmd_fild02 | 162 | 1 |
| 150 | Indian Fillet | 4,000 | 4,600 | 10,600 | uncommon | low | Goblin | 1,886 | 44 | gef_fild11 | 58 | 2 |
| 151 | Waghnak | 4,200 | 4,800 | 7,600 | uncommon | unknown | Wootan Fighter | 4,240 | 67 | um_fild02 | 68 | 2 |
| 152 | Dirk | 4,500 | 5,200 | 8,100 | uncommon | none | Goblin | 2,214 | 48 | gef_fild11 | 58 | 5 |
| 153 | High Heels | 4,500 | 5,200 | 8,100 | uncommon | unknown | Carat | 21,626 | 103 | gl_cas01 | 50 | 3 |
| 154 | Silk Ribbon | 4,500 | 5,200 | 11,900 | uncommon | medium | Sting | 25,266 | 104 | gl_sew03 | 99 | 5 |
| 155 | Fisherman's Dagger | 5,700 | 6,600 | 9,500 | uncommon | low | Piranha | 8,438 | 75 | bra_dun01 | 80 | 3 |
| 156 | Coco Card | 5,700 | 6,600 | 15,100 | uncommon | low | Coco | 1,388 | 38 | gef_fild02 | 172 | 1 |
| 157 | Old Card Album | 7,100 | 8,100 | 9,500 | uncommon | high | Nightmare Wander Man | 261,364 | 151 | gl_cas02_ | 60 | 2 |
| 158 | Flail | 8,400 | 9,700 | 15,200 | uncommon | unknown | Goblin | 1,886 | 44 | gef_fild11 | 58 | 5 |
| 159 | Beetle King Card | 8,400 | 9,700 | 22,400 | uncommon | low | Beetle King | 2,974 | 55 | mjolnir_08 | 169 | 1 |
| 160 | Transparent Plate | 8,400 | 9,700 | 18,700 | uncommon | unknown | Dimik | 43,030 | 116 | jupe_core | 40 | 25 |
| 161 | Transparent Plate | 8,400 | 9,700 | 18,700 | uncommon | unknown | Dimik | 52,088 | 116 | jupe_core | 40 | 25 |
| 162 | Level 6 Cookbook | 8,500 | 9,800 | 18,800 | uncommon | unknown | Orc Lady | 2,290 | 45 | gef_fild03 | 160 | 2 |
| 163 | Transparent Plate | 8,700 | 10,000 | 19,300 | uncommon | unknown | Dimik | 38,500 | 116 | jupe_core | 40 | 25 |
| 164 | Ambernite Card | 8,800 | 10,100 | 23,500 | uncommon | low | Ambernite | 530 | 19 | prt_fild04 | 111 | 1 |
| 165 | Transparent Plate | 8,800 | 10,100 | 19,600 | uncommon | unknown | Dimik | 47,558 | 116 | jupe_core | 40 | 25 |
| 166 | Crystal of Darkness | 8,800 | 10,100 | 14,700 | uncommon | high | Furious Incarnation of M | 639,000 | 132 | moc_fild22 | 3 | 2500 |
| 167 | Cyclone | 9,200 | 10,600 | 16,600 | uncommon | unknown | Firelock Soldier | 13,026 | 88 | ama_dun01 | 63 | 3 |
| 168 | Windhawk | 9,400 | 10,800 | 17,100 | uncommon | medium | Armeyer Dinze | 93,756 | 134 | lhz_dun02 | 50 | 5 |
| 169 | Poison Spore Card | 9,700 | 11,200 | 25,800 | uncommon | medium | Poison Spore | 758 | 26 | mjolnir_06 | 100 | 1 |
| 170 | Garnet | 10,100 | 11,600 | 22,500 | uncommon | unknown | Dragon Egg | 55,652 | 119 | hu_fild02 | 25 | 5 |
| 171 | Stiletto | 10,200 | 11,700 | 18,500 | uncommon | unknown | Sohee | 5,056 | 64 | pay_dun03 | 70 | 3 |
| 172 | Sleeper Card | 11,000 | 12,600 | 29,200 | uncommon | medium | Sleeper | 9,010 | 81 | yuno_fild02 | 185 | 1 |
| 173 | Shell Fish Card | 11,200 | 12,900 | 29,900 | uncommon | low | Shellfish | 2,652 | 50 | hu_fild06 | 87 | 1 |
| 174 | Bastard Sword | 11,800 | 13,600 | 21,400 | uncommon | unknown | Tamruan | 7,434 | 73 | ayo_dun02 | 116 | 4 |
| 175 | Chain | 12,100 | 13,900 | 21,800 | uncommon | unknown | Marine Sphere | 3,662 | 51 | iz_dun03 | 20 | 5 |
| 176 | Dusk | 12,300 | 14,100 | 22,300 | uncommon | unknown | Dimik | 43,030 | 116 | jupe_core | 40 | 3 |
| 177 | Nurse Cap | 13,000 | 14,900 | 34,800 | uncommon | low | Sohee | 5,056 | 64 | pay_dun03 | 70 | 1 |
| 178 | Icicle Fist | 13,200 | 15,200 | 35,300 | uncommon | low | Snowier | 28,454 | 103 | ice_dun02 | 70 | 2 |
| 179 | Blade Lost in Darkness | 13,700 | 15,800 | 30,400 | uncommon | unknown | Abysmal Knight | 69,372 | 122 | gl_knt01 | 14 | 3 |
| 180 | False Angel Card | 13,900 | 16,000 | 37,000 | uncommon | low | False Angel | 20,862 | 105 | gefenia01 | 63 | 1 |
| 181 | Zircon | 2,400 | 2,800 | 4,300 | scarce | unknown | Smokie | 828 | 29 | mjolnir_06 | 70 | 1 |
| 182 | Demon Pungus Card | 3,400 | 3,900 | 9,100 | scarce | low | Demon Pungus | 12,568 | 91 | ein_fild04 | 18 | 1 |
| 183 | Cap | 6,300 | 7,200 | 11,400 | scarce | unknown | Dragon Tail | 10,434 | 86 | tur_dun01 | 25 | 1 |
| 184 | Raccoon Doll | 12,300 | 14,100 | 27,300 | scarce | unknown | Smokie | 828 | 29 | mjolnir_06 | 70 | 1 |
| 185 | Red Feather | 14,200 | 16,300 | 31,600 | scarce | unknown | Furious Baroness of Retr | 316,630 | 121 | tha_t10 | 2 | 1000 |
| 186 | Ring | 15,800 | 18,200 | 28,500 | scarce | medium | Incubus | 50,856 | 120 | gefenia03 | 21 | 1 |
| 187 | Executioner's Mitten | 17,100 | 19,700 | 37,900 | scarce | unknown | Rybio | 19,878 | 98 | gl_prison | 19 | 2 |
| 188 | Blue Feather | 17,300 | 19,900 | 38,400 | scarce | unknown | Dame of Sentinel Ringlea | 368,440 | 127 | tha_t12 | 2 | 1250 |
| 189 | Transparent Head Protector | 17,400 | 20,000 | 46,500 | scarce | medium | Marine Sphere | 3,662 | 51 | iz_dun03 | 20 | 5 |
| 190 | Fashion Glasses | 22,200 | 25,500 | 49,300 | scarce | unknown | Sage Worm | 4,858 | 70 | gl_cas01 | 17 | 5 |
| 191 | Sword Mace | 26,200 | 30,100 | 47,500 | scarce | low | Dokebi | 5,122 | 68 | pay_dun04 | 40 | 1 |
| 192 | Padded Armor | 27,400 | 31,500 | 45,600 | scarce | none | Rotar Zairo | 2,580 | 48 | prt_fild11 | 50 | 1 |
| 193 | Cruiser Card | 27,400 | 31,500 | 73,200 | scarce | low | Cruiser | 1,842 | 41 | xmas_dun02 | 49 | 1 |
| 194 | Myst Card | 28,700 | 33,000 | 76,500 | scarce | low | Myst | 2,808 | 49 | mjo_dun03 | 39 | 1 |
| 195 | Ora Ora | 28,900 | 26,400 | 31,100 | scarce | unknown | Tarou | 570 | 22 | mjo_dun01 | 63 | 1 |
| 196 | Seyren Windsor Card | 32,900 | 37,800 | 87,800 | scarce | low | Seyren Windsor | 409,924 | 142 | lhz_dun03 | 42 | 1 |
| 197 | Eye of Dullahan | 47,200 | 54,300 | 84,100 | scarce | low | Dullahan | 32,982 | 108 | nif_fild01 | 22 | 1 |
| 198 | Blazer Card | 48,600 | 55,900 | 130,000 | scarce | medium | Blazer | 19,006 | 101 | mag_dun01 | 20 | 1 |
| 199 | Poisonous Toad Card | 49,000 | 56,300 | 131,000 | scarce | low | Poisonous Toad | 11,154 | 87 | ama_dun02 | 35 | 1 |
| 200 | Hammer of Blacksmith | 50,000 | 57,500 | 174,000 | scarce | none | Dokebi | 5,122 | 68 | pay_dun04 | 40 | 3 |
