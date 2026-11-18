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
  "missionPayoutAvg": 1022640,
  "missionPayoutMin": 780000,
  "missionPayoutMax": 1368000,
  "missionQtyMin": 5,
  "missionQtyMax": 300,
  "missionRatioAvg": 1.989,
  "weightLimited": 9
}
```

## Missions

| # | Tier | Item | Qty | Canonical buy | Garrett unit | Payout | Buy value | Mob | HP | Mob lvl | Abundance | Difficulty | Partial | Forfeit |
|---:|---|---|---:|---:|---:|---:|---:|---|---:|---:|---|---|---|---|
| 1 | common | Inside-out Shirt | 91 | 4,400 | 8,800 | 801,000 | 400,400 | Wakwak | 35,738 | 111 | abundant | easy | yes | yes |
| 2 | common | Fine Grit | 236 | 1,700 | 3,400 | 802,000 | 401,200 | Scorpion | 272 | 16 | abundant | easy | yes | yes |
| 3 | common | Oil Paper | 191 | 2,100 | 4,200 | 802,000 | 401,100 | Karakasa | 6,054 | 72 | abundant | easy | yes | yes |
| 4 | common | Solid Trunk | 253 | 1,600 | 3,200 | 810,000 | 404,800 | Willow | 156 | 8 | abundant | easy | yes | yes |
| 5 | common | Clam Flesh | 83 | 4,900 | 9,800 | 813,000 | 406,700 | Red Eruma | 16,058 | 91 | abundant | easy | yes | yes |
| 6 | common | Mysterious Flower | 87 | 4,700 | 9,400 | 818,000 | 408,900 | Tiyanak | 23,178 | 105 | abundant | easy | yes | yes |
| 7 | common | Barren Trunk | 256 | 1,600 | 3,200 | 819,000 | 409,600 | Willow | 156 | 8 | abundant | easy | yes | yes |
| 8 | common | Rainbow Shell | 205 | 2,000 | 4,000 | 820,000 | 410,000 | Stainer | 424 | 21 | abundant | easy | yes | yes |
| 9 | common | Lantern | 300 | 1,300 | 2,600 | 780,000 | 390,000 | Skeleton Worker | 2,302 | 44 | abundant | easy | yes | yes |
| 10 | common | Bug Leg | 300 | 1,300 | 2,600 | 780,000 | 390,000 | Argiope | 7,140 | 75 | abundant | easy | yes | yes |
| 11 | common | Worn Out Page | 72 | 5,700 | 11,400 | 821,000 | 410,400 | Rideword | 5,710 | 74 | abundant | easy | yes | yes |
| 12 | common | Elegant Flower | 54 | 7,600 | 15,200 | 821,000 | 410,400 | Mangkukulam | 29,114 | 110 | abundant | easy | yes | yes |
| 13 | common | Strong Vine | 98 | 4,200 | 8,400 | 823,000 | 411,600 | Nepenthes | 36,410 | 114 | abundant | easy | yes | yes |
| 14 | common | Slick Paper | 243 | 1,700 | 3,400 | 826,000 | 413,100 | Karakasa | 6,054 | 72 | abundant | easy | yes | yes |
| 15 | common | Heart of Mermaid | 300 | 1,400 | 2,800 | 840,000 | 420,000 | Iara | 8,524 | 79 | abundant | easy | yes | yes |
| 16 | common | Blue Hair | 300 | 1,400 | 2,800 | 840,000 | 420,000 | Kobold Archer | 22,944 | 108 | abundant | easy | yes | yes |
| 17 | common | Spawn | 184 | 2,300 | 4,600 | 846,000 | 423,200 | Comodo | 8,582 | 81 | abundant | easy | yes | yes |
| 18 | common | Fine Sand | 212 | 2,000 | 4,000 | 848,000 | 424,000 | Sleeper | 9,010 | 81 | abundant | easy | yes | yes |
| 19 | common | Porcupine Quill | 205 | 2,100 | 4,200 | 861,000 | 430,500 | Caramel | 638 | 25 | abundant | easy | yes | yes |
| 20 | common | Dokebi Horn | 37 | 11,800 | 23,600 | 873,000 | 436,600 | Dokebi | 5,122 | 68 | abundant | easy | yes | yes |
| 21 | uncommon | Hinalle | 128 | 4,100 | 8,200 | 1,050,000 | 524,800 | Rocker | 310 | 15 | common | easy | yes | yes |
| 22 | uncommon | Burnt Part | 175 | 3,000 | 6,000 | 1,050,000 | 525,000 | Alicel | 36,638 | 115 | abundant | medium | yes | yes |
| 23 | uncommon | Ment | 31 | 16,900 | 33,800 | 1,048,000 | 523,900 | Rafflesia | 9,884 | 86 | common | easy | yes | yes |
| 24 | uncommon | Munak Doll | 37 | 14,100 | 28,200 | 1,043,000 | 521,700 | Yao Jun | 12,826 | 87 | common | easy | yes | yes |
| 25 | uncommon | Turtle Shell | 200 | 2,600 | 5,200 | 1,040,000 | 520,000 | Assaulter | 17,544 | 100 | abundant | medium | yes | yes |
| 26 | uncommon | Old Magicbook | 113 | 4,700 | 9,400 | 1,062,000 | 531,100 | Rideword | 5,710 | 74 | common | medium | yes | yes |
| 27 | uncommon | Wedding Veil | 50 | 12,100 | 20,700 | 1,035,000 | 605,000 | Nightmare Wraith Dead | 37,846 | 110 | common | easy | yes | yes |
| 28 | uncommon | 2carat Diamond | 22 | 24,400 | 48,800 | 1,074,000 | 536,800 | Wraith | 8,830 | 77 | common | medium | yes | yes |
| 29 | uncommon | Puppy Headband | 50 | 10,800 | 21,600 | 1,080,000 | 540,000 | Kobold Archer | 22,944 | 108 | common | easy | yes | yes |
| 30 | uncommon | Steel Arrow Quiver | 20 | 25,500 | 51,000 | 1,020,000 | 510,000 | Kavach Icarus | 86,158 | 135 | common | medium | yes | yes |
| 31 | uncommon | Rotten Meat | 11 | 50,000 | 100,000 | 1,100,000 | 550,000 | Roween | 13,234 | 95 | abundant | medium | yes | yes |
| 32 | uncommon | Silent Energy Particle | 169 | 3,300 | 6,600 | 1,115,000 | 557,700 | Remover | 66,204 | 121 | abundant | medium | yes | yes |
| 33 | uncommon | Gas Mask | 38 | 14,700 | 29,400 | 1,117,000 | 558,600 | Remover | 66,204 | 121 | common | medium | yes | yes |
| 34 | uncommon | Deadly Noxious Herb | 65 | 8,600 | 17,200 | 1,118,000 | 559,000 | Marina | 2,020 | 42 | common | easy | yes | yes |
| 35 | uncommon | Dew Laden Moss | 100 | 5,600 | 11,200 | 1,120,000 | 560,000 | Plankton | 1,866 | 40 | common | easy | yes | yes |
| 36 | uncommon | Pet Incubator | 126 | 5,200 | 9,000 | 1,134,000 | 655,200 | Eggyra | 2,472 | 53 | common | easy | yes | yes |
| 37 | uncommon | Rusty Iron | 76 | 7,500 | 15,000 | 1,140,000 | 570,000 | Scorpion | 272 | 16 | common | easy | yes | yes |
| 38 | uncommon | Clown Nose | 50 | 9,600 | 19,200 | 960,000 | 480,000 | Lunatic | 96 | 3 | common | easy | yes | yes |
| 39 | uncommon | Rusty Arrow Quiver | 20 | 24,000 | 48,000 | 960,000 | 480,000 | Kobold Archer | 22,944 | 108 | common | easy | yes | yes |
| 40 | uncommon | Cursed Ruby | 50 | 11,500 | 23,000 | 1,150,000 | 575,000 | Gibbet | 27,810 | 105 | common | medium | yes | yes |
| 41 | rare | Fin | 13 | 50,000 | 100,000 | 1,300,000 | 650,000 | Strouf | 5,492 | 61 | abundant | hard | yes | yes |
| 42 | rare | Level 8 Cookbook | 13 | 50,000 | 100,000 | 1,300,000 | 650,000 | Death Word | 36,410 | 114 | uncommon | medium | yes | yes |
| 43 | rare | Level 9 Cookbook | 13 | 50,000 | 100,000 | 1,300,000 | 650,000 | Death Word | 36,410 | 114 | uncommon | easy | yes | yes |
| 44 | rare | Nurse Cap | 50 | 13,000 | 26,000 | 1,300,000 | 650,000 | Sohee | 5,056 | 64 | uncommon | easy | yes | yes |
| 45 | rare | Level 7 Cookbook | 15 | 43,200 | 86,400 | 1,296,000 | 648,000 | Evil Druid | 9,440 | 80 | uncommon | easy | yes | yes |
| 46 | rare | Necklace of Oblivion | 30 | 22,500 | 45,000 | 1,350,000 | 675,000 | Jakk | 3,802 | 63 | uncommon | easy | yes | yes |
| 47 | rare | Stainer Card | 5 | 135,000 | 270,000 | 1,350,000 | 675,000 | Stainer | 424 | 21 | uncommon | easy | yes | yes |
| 48 | rare | Elixir Bandages | 41 | 16,500 | 33,000 | 1,353,000 | 676,500 | Evil Druid | 9,440 | 80 | uncommon | easy | yes | yes |
| 49 | rare | Aerial | 28 | 24,200 | 48,400 | 1,355,000 | 677,600 | Deviace | 4,648 | 60 | rare | easy | yes | yes |
| 50 | rare | Icicle Staff | 6 | 114,000 | 228,000 | 1,368,000 | 684,000 | Ice Ghost | 4,836,630 | 189 | common | extreme | yes | yes |

## Offers

| # | Item | Canonical buy | Garrett buy | Mid | Abundance | Demand | Mob | HP | Mob lvl | Map | Spawn | Drop |
|---:|---|---:|---:|---:|---|---|---|---:|---:|---|---:|---:|
| 1 | Aloe Leaflet | 253 | 506 | 422 | abundant | high | Grove | 3,468 | 55 | cmd_fild01 | 202 | 750 |
| 2 | Yellow Herb | 254 | 508 | 725 | abundant | high | Goat | 5,810 | 80 | yuno_fild11 | 139 | 1250 |
| 3 | Dragon Canine | 254 | 508 | 254 | abundant | medium | Petite | 10,982 | 86 | gef_fild06 | 158 | 2668 |
| 4 | Solid Shell | 257 | 514 | 429 | abundant | low | Luciola Vespa | 26,008 | 109 | spl_fild03 | 74 | 1500 |
| 5 | Explosive Powder | 262 | 524 | 262 | abundant | low | Sting | 25,266 | 104 | gl_sew03 | 99 | 400 |
| 6 | Red Herb | 263 | 526 | 751 | abundant | high | Spore | 446 | 18 | pay_fild08 | 148 | 1000 |
| 7 | Peaked Hat | 282 | 564 | 469 | abundant | high | Tatacho | 73,942 | 128 | man_fild02 | 37 | 1500 |
| 8 | Fluff | 301 | 602 | 860 | abundant | high | Fabre | 118 | 6 | prt_fild06 | 149 | 7000 |
| 9 | Mould Powder | 302 | 604 | 864 | abundant | medium | Punk | 6,996 | 82 | c_tower1 | 107 | 2668 |
| 10 | Memento | 315 | 540 | 570 | abundant | none | Zombie Slaughter | 69,962 | 124 | abbey02 | 210 | 750 |
| 11 | Frill | 317 | 634 | 528 | abundant | high | Driller | 4,726 | 65 | mjolnir_04 | 162 | 3750 |
| 12 | Orc's Fang | 319 | 638 | 532 | abundant | low | Orc Skeleton | 3,398 | 53 | orcsdun02 | 50 | 2750 |
| 13 | Rough Elunium | 341 | 682 | 543 | abundant | medium | Argiope | 7,140 | 75 | mjolnir_11 | 170 | 88 |
| 14 | Orc Claw | 343 | 686 | 572 | abundant | low | Orc Zombie | 3,172 | 51 | orcsdun01 | 80 | 2750 |
| 15 | Gun Powder | 343 | 686 | 980 | abundant | low | Pitman | 13,434 | 90 | ein_dun01 | 70 | 450 |
| 16 | Antelope Horn | 353 | 605 | 356 | abundant | unknown | Goat | 5,810 | 80 | yuno_fild11 | 139 | 2280 |
| 17 | Fang | 357 | 714 | 357 | abundant | medium | Orc Archer | 6,948 | 78 | alde_dun02 | 20 | 2328 |
| 18 | Mushroom Spore | 358 | 716 | 478 | abundant | high | Spore | 446 | 18 | pay_fild08 | 148 | 8000 |
| 19 | Cactus Needle | 362 | 724 | 482 | abundant | high | Muka | 674 | 23 | moc_fild01 | 202 | 4500 |
| 20 | Fresh Fish | 368 | 630 | 368 | abundant | low | Ferus | 84,448 | 126 | abyss_01 | 55 | 2550 |
| 21 | Fur | 370 | 740 | 496 | abundant | high | Tatacho | 73,942 | 128 | man_fild02 | 37 | 2000 |
| 22 | Horn of Hillslion | 371 | 742 | 618 | abundant | low | Hillthrion | 52,252 | 123 | man_fild03 | 33 | 1500 |
| 23 | Brigan | 392 | 784 | 392 | abundant | high | Raydric | 43,962 | 115 | gl_knt01 | 126 | 2425 |
| 24 | Cyfar | 405 | 810 | 481 | abundant | medium | Orc Lady | 2,290 | 45 | gef_fild03 | 160 | 2328 |
| 25 | Round Shell | 410 | 820 | 419 | abundant | high | Arclouze | 29,888 | 107 | alde_dun01 | 58 | 1750 |
| 26 | Peco Peco Feather | 416 | 832 | 1,100 | abundant | none | Grand Peco | 6,168 | 75 | yuno_fild09 | 182 | 2425 |
| 27 | Burning Horseshoe | 432 | 864 | 432 | abundant | low | Headless Mule | 6,536 | 80 | bra_fild01 | 40 | 2000 |
| 28 | Nose Ring | 441 | 882 | 736 | abundant | unknown | Majoruros | 27,044 | 107 | gl_dun02 | 52 | 2207 |
| 29 | Solid Iron Piece | 443 | 886 | 1,200 | abundant | none | Alicel | 36,638 | 115 | kh_dun02 | 41 | 1500 |
| 30 | White Herb | 448 | 896 | 597 | abundant | high | Stem Worm | 8,168 | 84 | lhz_fild02 | 100 | 900 |
| 31 | Wolf Claw | 451 | 902 | 1,200 | abundant | low | Wolf | 2,182 | 45 | moc_fild03 | 164 | 4500 |
| 32 | Nipper | 474 | 948 | 790 | abundant | none | Vadon | 2,182 | 45 | iz_dun01 | 60 | 4500 |
| 33 | Clover | 487 | 974 | 811 | abundant | medium | Lunatic | 96 | 3 | prt_fild01 | 196 | 7000 |
| 34 | Monster Blood | 488 | 976 | 814 | abundant | none | Fire Sandman | 261,002 | 143 | moro_vol | 30 | 1500 |
| 35 | Rusty Screw | 507 | 1,000 | 676 | abundant | high | Teddy Bear | 12,568 | 91 | ein_fild03 | 100 | 1900 |
| 36 | Bow | 525 | 900 | 950 | abundant | medium | Condor | 210 | 12 | moc_fild11 | 137 | 100 |
| 37 | Well-baked Cookie | 528 | 1,100 | 1,200 | abundant | unknown | Christmas Cookie | 1,322 | 37 | xmas_dun01 | 49 | 2000 |
| 38 | Honey | 529 | 1,100 | 1,500 | abundant | high | Teddy Bear | 12,568 | 91 | ein_fild03 | 100 | 500 |
| 39 | Delicious Jelly | 544 | 1,100 | 1,200 | abundant | unknown | Siorava | 11,154 | 87 | mal_dun01 | 45 | 700 |
| 40 | Venom Canine | 549 | 1,100 | 732 | abundant | high | Anacondaq | 18,466 | 100 | ra_fild08 | 159 | 4500 |
| 41 | Glass Bead | 551 | 945 | 998 | abundant | none | Sea Otter | 2,948 | 48 | cmd_fild04 | 149 | 325 |
| 42 | Yam | 558 | 1,100 | 1,200 | abundant | unknown | Grizzly | 4,370 | 66 | lou_dun01 | 17 | 1250 |
| 43 | Rice Cake | 566 | 1,100 | 1,300 | abundant | unknown | Taoist Hermit | 19,454 | 96 | gon_dun03 | 40 | 2250 |
| 44 | Emveretarcon | 570 | 900 | 950 | abundant | medium | Mineral | 15,918 | 96 | ein_dun02 | 50 | 400 |
| 45 | Harpy Feather | 600 | 1,200 | 600 | abundant | none | Harpy | 8,908 | 83 | yuno_fild03 | 174 | 2425 |
| 46 | Green Herb | 612 | 1,200 | 816 | abundant | high | Fabre | 118 | 6 | prt_fild06 | 149 | 3000 |
| 47 | Concentration Potion | 630 | 1,100 | 630 | abundant | medium | Raggler | 1,970 | 48 | cmd_fild07 | 116 | 100 |
| 48 | Short Daenggie | 646 | 1,300 | 1,700 | abundant | none | Bongun | 4,130 | 59 | pay_dun02 | 30 | 2750 |
| 49 | Worn-out Prison Uniform | 654 | 1,300 | 1,700 | abundant | none | Alligator | 3,878 | 57 | cmd_fild03 | 194 | 300 |
| 50 | Dark Crystal Fragment | 670 | 1,300 | 1,900 | abundant | low | Obsidian | 16,984 | 97 | ein_dun02 | 40 | 1500 |
| 51 | Blue Herb | 676 | 1,400 | 901 | abundant | high | Goat | 5,810 | 80 | yuno_fild11 | 139 | 500 |
| 52 | Log | 676 | 1,400 | 1,800 | abundant | medium | Stone Shooter | 3,680 | 64 | um_fild01 | 40 | 2500 |
| 53 | Scorpion Tail | 697 | 1,400 | 1,200 | abundant | high | Scorpion | 272 | 16 | moc_fild18 | 160 | 2750 |
| 54 | Worm Peeling | 704 | 1,400 | 1,900 | abundant | low | Andre | 1,074 | 33 | cmd_fild08 | 62 | 4500 |
| 55 | Steel | 712 | 900 | 950 | abundant | high | Pitman | 13,434 | 90 | ein_dun01 | 70 | 250 |
| 56 | Squid Ink | 725 | 1,400 | 1,200 | abundant | none | Sedora | 33,480 | 110 | iz_dun05 | 60 | 1500 |
| 57 | Grit | 737 | 1,500 | 1,200 | abundant | none | Sleeper | 9,010 | 81 | yuno_fild02 | 185 | 2668 |
| 58 | Antelope Skin | 751 | 1,500 | 2,000 | abundant | none | Goat | 5,810 | 80 | yuno_fild11 | 139 | 1250 |
| 59 | Earthworm Peeling | 768 | 1,500 | 2,200 | abundant | high | Hode | 4,694 | 63 | moc_fild17 | 170 | 4500 |
| 60 | Nine Tails | 774 | 1,500 | 2,200 | abundant | high | Nine Tail | 4,844 | 72 | pay_dun04 | 30 | 2328 |
| 61 | Flexible Tube | 780 | 1,600 | 2,200 | abundant | none | Metaling | 7,724 | 81 | ein_fild08 | 139 | 2000 |
| 62 | Oridecon | 784 | 990 | 1,000 | abundant | high | Big Bell | 333,720 | 163 | c_tower3_ | 109 | 100 |
| 63 | Elunium | 784 | 990 | 1,000 | abundant | high | Banaspaty | 6,470 | 85 | dew_dun02 | 70 | 750 |
| 64 | Star Dust | 788 | 1,400 | 1,400 | abundant | medium | Sandman | 4,648 | 61 | moc_fild16 | 130 | 100 |
| 65 | Trunk | 822 | 1,600 | 2,300 | abundant | medium | Greatest General | 2,810 | 55 | pay_fild10 | 129 | 1000 |
| 66 | Light Granule | 855 | 1,400 | 1,400 | abundant | high | Hillthrion | 52,252 | 123 | man_fild03 | 33 | 600 |
| 67 | Coral Reef | 871 | 1,700 | 2,500 | abundant | high | Penomena | 9,242 | 85 | alde_dun03 | 85 | 2425 |
| 68 | Research Chart | 899 | 1,800 | 1,500 | abundant | medium | Gertie | 533,852 | 141 | lhz_dun04 | 57 | 2000 |
| 69 | Horrendous Hair | 915 | 1,800 | 1,200 | abundant | high | Medusa | 22,560 | 102 | beach_dun | 60 | 2668 |
| 70 | Pointed Scale | 979 | 2,000 | 1,600 | abundant | none | Wormtail | 372 | 17 | pay_fild06 | 140 | 2750 |
| 71 | Hat | 525 | 900 | 525 | common | unknown | Spore | 446 | 18 | pay_fild08 | 148 | 30 |
| 72 | Hat | 525 | 900 | 950 | common | low | Poison Spore | 758 | 26 | mjolnir_06 | 100 | 10 |
| 73 | Adventurer's Suit | 525 | 900 | 537 | common | unknown | Munak | 4,004 | 58 | pay_dun02 | 40 | 50 |
| 74 | Adventurer's Suit | 570 | 900 | 950 | common | none | Baby Desert Wolf | 226 | 14 | moc_fild11 | 137 | 40 |
| 75 | Candy Cane | 618 | 1,200 | 1,800 | common | low | Cookie | 1,194 | 35 | xmas_dun01 | 49 | 75 |
| 76 | Sunflower | 770 | 1,500 | 2,100 | common | low | Geographer | 6,816 | 73 | yuno_fild01 | 75 | 15 |
| 77 | Falchion | 788 | 1,400 | 1,400 | common | medium | Pirate Skeleton | 2,702 | 48 | treasure01 | 56 | 125 |
| 78 | Flower Ring | 788 | 1,400 | 788 | common | unknown | Toucan | 5,128 | 70 | bra_fild01 | 60 | 100 |
| 79 | Mace | 840 | 1,400 | 1,500 | common | medium | Curupira | 5,122 | 68 | bra_fild01 | 50 | 50 |
| 80 | Egg | 852 | 1,700 | 1,900 | common | unknown | Leshij | 9,440 | 81 | mosk_dun01 | 74 | 25 |
| 81 | Spear | 892 | 1,500 | 1,600 | common | low | Mandragora | 280 | 13 | gef_fild04 | 125 | 30 |
| 82 | Level 5 Fire Wall | 1,000 | 2,000 | 1,000 | common | none | Marionette | 8,178 | 90 | gef_dun02 | 30 | 50 |
| 83 | Katana | 1,000 | 1,800 | 1,900 | common | medium | Boa | 406 | 18 | pay_fild02 | 142 | 20 |
| 84 | Singing Plant | 1,100 | 2,200 | 1,800 | common | medium | Mavka | 9,980 | 84 | mosk_dun03 | 17 | 150 |
| 85 | Red Frame | 1,200 | 2,000 | 1,200 | common | unknown | Dark Frame | 7,306 | 76 | gl_cas01 | 35 | 500 |
| 86 | Main Gauche | 1,300 | 2,200 | 2,300 | common | low | Poporing | 978 | 30 | pay_fild04 | 141 | 20 |
| 87 | Main Gauche | 1,300 | 2,200 | 2,300 | common | high | Hornet | 170 | 11 | prt_fild05 | 199 | 20 |
| 88 | Wand | 1,300 | 2,200 | 2,400 | common | unknown | Goblin | 3,754 | 56 | prt_fild11 | 60 | 8 |
| 89 | Composite Bow | 1,300 | 2,200 | 2,400 | common | low | Goblin Archer | 2,974 | 55 | prt_fild11 | 50 | 13 |
| 90 | Red Bijou | 1,300 | 2,600 | 2,200 | common | low | Ferus | 69,764 | 126 | abyss_02 | 50 | 400 |
| 91 | Green Lace | 1,300 | 2,600 | 2,100 | common | medium | Wormtail | 372 | 17 | pay_fild06 | 140 | 50 |
| 92 | White Powder | 1,400 | 2,800 | 3,600 | common | none | Anacondaq | 18,466 | 100 | ra_fild08 | 159 | 100 |
| 93 | Cat's Eye | 1,400 | 2,800 | 3,900 | common | none | Mao Guai | 10,930 | 89 | lou_dun03 | 18 | 1000 |
| 94 | Green Bijou | 1,400 | 2,800 | 2,400 | common | low | Ferus | 84,448 | 126 | abyss_01 | 55 | 400 |
| 95 | Chivalry Emblem | 1,500 | 3,000 | 3,900 | common | medium | Raydric | 43,962 | 115 | gl_knt01 | 126 | 5 |
| 96 | Anodyne | 1,600 | 3,200 | 2,100 | common | medium | Noxious | 8,924 | 87 | ein_fild05 | 100 | 25 |
| 97 | Chonchon Doll | 1,600 | 2,700 | 2,400 | common | unknown | Chonchon | 96 | 5 | gef_fild00 | 160 | 6 |
| 98 | Peridot | 1,600 | 2,700 | 2,800 | common | unknown | Jewelry Ant | 4,891,312 | 191 | ein_dun03 | 20 | 750 |
| 99 | Blue Bijou | 1,600 | 3,200 | 2,100 | common | low | Acidus | 78,178 | 130 | abyss_02 | 60 | 400 |
| 100 | Yggdrasil Dust | 1,600 | 3,200 | 2,600 | common | low | Cenere | 260,262 | 146 | ecl_tdun01 | 15 | 500 |
| 101 | Pike | 1,800 | 3,100 | 3,300 | common | medium | Wormtail | 372 | 17 | pay_fild06 | 140 | 15 |
| 102 | Shoes | 1,800 | 3,200 | 3,300 | common | medium | Munak | 4,004 | 58 | pay_dun02 | 40 | 8 |
| 103 | Yellow Bijou | 1,800 | 3,600 | 2,900 | common | medium | Acidus | 81,900 | 130 | abyss_03 | 60 | 400 |
| 104 | Banana Juice | 2,000 | 4,000 | 101,000 | common | medium | Choco | 1,970 | 48 | um_fild02 | 8 | 500 |
| 105 | Emerald | 2,400 | 4,000 | 2,400 | common | none | Roda Frog | 280 | 13 | prt_fild00 | 169 | 8 |
| 106 | Sapphire | 2,400 | 4,000 | 2,400 | common | none | Sea Otter | 2,948 | 48 | cmd_fild04 | 149 | 25 |
| 107 | Bizarre Stone Carvings | 2,400 | 4,800 | 3,900 | common | none | Green Mineral | 4,871,404 | 190 | ein_dun03 | 40 | 150 |
| 108 | Blue Potion | 2,700 | 4,500 | 3,600 | common | high | Dark Priest | 21,686 | 98 | gl_chyard | 95 | 50 |
| 109 | Yggdrasil Berry | 2,800 | 4,500 | 4,800 | common | high | Combat Basilisk | 432,072 | 148 | lasa_dun03 | 110 | 80 |
| 110 | Battle Axe | 2,800 | 4,900 | 5,100 | common | low | Orc Warrior | 2,094 | 44 | gef_fild10 | 179 | 5 |
| 111 | Amethyst | 3,200 | 5,400 | 3,200 | common | high | Argiope | 7,140 | 75 | mjolnir_11 | 170 | 5 |
| 112 | Pearl | 3,200 | 5,400 | 5,700 | common | medium | Sea Otter | 2,948 | 48 | cmd_fild04 | 149 | 75 |
| 113 | Sardonyx | 3,200 | 6,400 | 3,200 | common | none | Drainliar | 2,364 | 47 | alde_dun03 | 55 | 10 |
| 114 | Opal | 3,200 | 6,400 | 3,200 | common | low | Zombie | 408 | 17 | pay_dun00 | 40 | 70 |
| 115 | Topaz | 3,200 | 4,000 | 4,300 | common | medium | Mineral | 15,918 | 96 | ein_dun02 | 50 | 250 |
| 116 | Aquamarine | 3,400 | 5,400 | 5,700 | common | high | Merman | 4,648 | 60 | iz_dun04 | 61 | 20 |
| 117 | Yggdrasil Seed | 3,600 | 4,500 | 4,800 | common | high | Stem Worm | 8,168 | 84 | lhz_fild02 | 100 | 5 |
| 118 | Claw of Monkey | 3,600 | 7,200 | 8,100 | common | unknown | Choco | 1,970 | 48 | um_fild02 | 8 | 2668 |
| 119 | Silver Robe | 3,700 | 7,400 | 5,900 | common | low | Laurell Weinder | 80,564 | 133 | lhz_dun02 | 50 | 15 |
| 120 | 1carat Diamond | 3,900 | 6,800 | 7,100 | common | none | Obsidian | 16,984 | 97 | ein_dun02 | 40 | 250 |
| 121 | Coconut Fruit | 3,900 | 7,800 | 8,600 | common | unknown | Galapago | 1,964 | 45 | cmd_fild02 | 40 | 150 |
| 122 | Folding Fan of Cat Ghost | 3,900 | 7,800 | 8,700 | common | unknown | Mao Guai | 10,930 | 89 | lou_dun03 | 18 | 2086 |
| 123 | Little Ghost Doll | 3,900 | 7,800 | 8,600 | common | unknown | Zhu Po Long | 8,308 | 82 | lou_dun03 | 30 | 400 |
| 124 | Red Chile | 3,900 | 7,800 | 8,700 | common | unknown | Kraben | 4,318 | 70 | ayo_dun02 | 23 | 500 |
| 125 | Gift Box | 4,000 | 8,000 | 5,300 | common | high | Ancient Mimic | 39,556 | 112 | tha_t02 | 80 | 25 |
| 126 | Old Manteau | 4,000 | 8,000 | 8,900 | common | unknown | Bloody Murderer | 34,934 | 110 | nif_fild02 | 11 | 2086 |
| 127 | Crest Piece | 4,000 | 8,000 | 9,000 | common | unknown | Venatu | 36,184 | 113 | juperos_01 | 70 | 175 |
| 128 | White Mask | 4,000 | 8,000 | 9,000 | common | unknown | Aunoe | 29,114 | 110 | arug_dun01 | 22 | 1250 |
| 129 | Crest Piece | 4,100 | 8,200 | 9,000 | common | unknown | Venatu | 37,992 | 113 | juperos_01 | 70 | 200 |
| 130 | Spore Doll | 4,200 | 8,400 | 11,100 | common | none | Spore | 446 | 18 | pay_fild08 | 148 | 10 |
| 131 | Silk Robe | 4,200 | 7,200 | 7,600 | common | high | Creamy | 494 | 23 | gef_fild05 | 143 | 20 |
| 132 | Oil Bottle | 4,200 | 8,400 | 9,200 | common | unknown | Venatu | 36,184 | 113 | juperos_01 | 70 | 50 |
| 133 | Savage Meat | 4,200 | 8,400 | 11,300 | common | medium | Savage | 4,316 | 59 | mjolnir_07 | 161 | 25 |
| 134 | Old Shuriken | 4,200 | 8,400 | 9,400 | common | unknown | Assaulter | 17,544 | 100 | tur_dun04 | 42 | 420 |
| 135 | Frilldora's Fiery Nape | 4,400 | 8,800 | 9,700 | common | unknown | Fire Frilldora | 282,602 | 147 | moro_vol | 30 | 1500 |
| 136 | Battered Kettle | 4,400 | 8,800 | 9,700 | common | unknown | Old Stove | 15,560 | 92 | ein_dun02 | 30 | 500 |
| 137 | Crest Piece | 4,400 | 8,800 | 9,700 | common | unknown | Venatu | 41,610 | 113 | juperos_01 | 50 | 150 |
| 138 | Crystalized Teardrop | 4,500 | 9,000 | 10,100 | common | unknown | Aqua Elemental | 74,840 | 121 | nyd_dun01 | 20 | 500 |
| 139 | Stone Of Blessing | 4,500 | 9,000 | 10,100 | common | unknown | Fire Golem | 360,426 | 148 | moro_vol | 30 | 2000 |
| 140 | Golem's Fiery Stone Tooth | 4,500 | 9,000 | 10,100 | common | unknown | Fire Golem | 360,426 | 148 | moro_vol | 30 | 1500 |
| 141 | China | 394 | 675 | 712 | uncommon | unknown | Peco Peco Egg | 140 | 7 | moc_fild12 | 45 | 5 |
| 142 | Aster Card | 429 | 858 | 1,100 | uncommon | low | Aster | 2,388 | 50 | hu_fild06 | 35 | 1 |
| 143 | Branch | 1,600 | 2,700 | 2,800 | uncommon | unknown | Cruiser | 1,842 | 41 | xmas_dun02 | 49 | 3 |
| 144 | Marin Card | 2,100 | 4,200 | 5,500 | uncommon | low | Marin | 1,688 | 37 | xmas_fild01 | 65 | 1 |
| 145 | Fragment of Darkness | 2,300 | 4,600 | 6,200 | uncommon | low | Furious Incarnation of M | 639,000 | 132 | moc_fild22 | 3 | 7500 |
| 146 | Ruby | 2,400 | 4,000 | 4,300 | uncommon | low | Furious Baroness of Retr | 316,630 | 121 | tha_t10 | 2 | 2500 |
| 147 | Muffler | 2,600 | 4,500 | 4,800 | uncommon | medium | Sohee | 5,056 | 64 | pay_dun03 | 70 | 3 |
| 148 | Sweet Roda Frog Card | 2,800 | 5,600 | 7,500 | uncommon | low | Sweet Roda Frog | 280 | 14 | lasa_fild02 | 100 | 10 |
| 149 | Flora Card | 3,400 | 6,800 | 9,200 | uncommon | low | Flora | 4,130 | 59 | cmd_fild01 | 67 | 1 |
| 150 | Scorpion Card | 3,700 | 7,400 | 9,900 | uncommon | low | Scorpion | 272 | 16 | moc_fild18 | 160 | 1 |
| 151 | Seal Card | 3,900 | 7,800 | 10,300 | uncommon | low | Seal | 2,600 | 47 | cmd_fild02 | 162 | 1 |
| 152 | Indian Fillet | 4,000 | 8,000 | 10,600 | uncommon | low | Goblin | 1,886 | 44 | gef_fild11 | 58 | 2 |
| 153 | Waghnak | 4,200 | 7,200 | 7,600 | uncommon | unknown | Wootan Fighter | 4,240 | 67 | um_fild02 | 68 | 2 |
| 154 | Dirk | 4,500 | 7,600 | 8,100 | uncommon | none | Goblin | 2,214 | 48 | gef_fild11 | 58 | 5 |
| 155 | High Heels | 4,500 | 7,600 | 8,100 | uncommon | unknown | Carat | 21,626 | 103 | gl_cas01 | 50 | 3 |
| 156 | Silk Ribbon | 4,500 | 9,000 | 11,900 | uncommon | medium | Sting | 25,266 | 104 | gl_sew03 | 99 | 5 |
| 157 | Comodo Card | 4,800 | 9,600 | 12,900 | uncommon | low | Comodo | 8,582 | 81 | dew_dun01 | 100 | 1 |
| 158 | Fisherman's Dagger | 5,700 | 9,000 | 9,500 | uncommon | low | Piranha | 8,438 | 75 | bra_dun01 | 80 | 3 |
| 159 | Coco Card | 5,700 | 11,400 | 15,100 | uncommon | low | Coco | 1,388 | 38 | gef_fild02 | 172 | 1 |
| 160 | Old Card Album | 7,100 | 9,000 | 9,500 | uncommon | high | Nightmare Wander Man | 261,364 | 151 | gl_cas02_ | 60 | 2 |
| 161 | Flail | 8,400 | 14,400 | 15,200 | uncommon | unknown | Goblin | 1,886 | 44 | gef_fild11 | 58 | 5 |
| 162 | Beetle King Card | 8,400 | 16,800 | 22,400 | uncommon | low | Beetle King | 2,974 | 55 | mjolnir_08 | 169 | 1 |
| 163 | Transparent Plate | 8,400 | 16,800 | 18,700 | uncommon | unknown | Dimik | 43,030 | 116 | jupe_core | 40 | 25 |
| 164 | Transparent Plate | 8,400 | 16,800 | 18,700 | uncommon | unknown | Dimik | 52,088 | 116 | jupe_core | 40 | 25 |
| 165 | Level 6 Cookbook | 8,500 | 17,000 | 18,800 | uncommon | unknown | Orc Lady | 2,290 | 45 | gef_fild03 | 160 | 2 |
| 166 | Transparent Plate | 8,700 | 17,400 | 19,300 | uncommon | unknown | Dimik | 38,500 | 116 | jupe_core | 40 | 25 |
| 167 | Ambernite Card | 8,800 | 17,600 | 23,500 | uncommon | low | Ambernite | 530 | 19 | prt_fild04 | 111 | 1 |
| 168 | Transparent Plate | 8,800 | 17,600 | 19,600 | uncommon | unknown | Dimik | 47,558 | 116 | jupe_core | 40 | 25 |
| 169 | Crystal of Darkness | 8,800 | 17,600 | 14,700 | uncommon | high | Furious Incarnation of M | 639,000 | 132 | moc_fild22 | 3 | 2500 |
| 170 | Cyclone | 9,200 | 15,800 | 16,600 | uncommon | unknown | Firelock Soldier | 13,026 | 88 | ama_dun01 | 63 | 3 |
| 171 | Windhawk | 9,400 | 16,200 | 17,100 | uncommon | medium | Armeyer Dinze | 93,756 | 134 | lhz_dun02 | 50 | 5 |
| 172 | Poison Spore Card | 9,700 | 19,400 | 25,800 | uncommon | medium | Poison Spore | 758 | 26 | mjolnir_06 | 100 | 1 |
| 173 | Garnet | 10,100 | 20,200 | 22,500 | uncommon | unknown | Dragon Egg | 55,652 | 119 | hu_fild02 | 25 | 5 |
| 174 | Stiletto | 10,200 | 17,600 | 18,500 | uncommon | unknown | Sohee | 5,056 | 64 | pay_dun03 | 70 | 3 |
| 175 | Sleeper Card | 11,000 | 22,000 | 29,200 | uncommon | medium | Sleeper | 9,010 | 81 | yuno_fild02 | 185 | 1 |
| 176 | Shell Fish Card | 11,200 | 22,400 | 29,900 | uncommon | low | Shellfish | 2,652 | 50 | hu_fild06 | 87 | 1 |
| 177 | Bastard Sword | 11,800 | 20,200 | 21,400 | uncommon | unknown | Tamruan | 7,434 | 73 | ayo_dun02 | 116 | 4 |
| 178 | Chain | 12,100 | 20,700 | 21,800 | uncommon | unknown | Marine Sphere | 3,662 | 51 | iz_dun03 | 20 | 5 |
| 179 | Dusk | 12,300 | 21,200 | 22,300 | uncommon | unknown | Dimik | 43,030 | 116 | jupe_core | 40 | 3 |
| 180 | Icicle Fist | 13,200 | 26,400 | 35,300 | uncommon | low | Snowier | 28,454 | 103 | ice_dun02 | 70 | 2 |
| 181 | Zircon | 2,400 | 4,000 | 4,300 | scarce | unknown | Smokie | 828 | 29 | mjolnir_06 | 70 | 1 |
| 182 | Demon Pungus Card | 3,400 | 6,800 | 9,100 | scarce | low | Demon Pungus | 12,568 | 91 | ein_fild04 | 18 | 1 |
| 183 | Galapago Card | 5,000 | 10,000 | 13,500 | scarce | low | Galapago | 1,964 | 45 | cmd_fild02 | 40 | 1 |
| 184 | Cap | 6,300 | 10,800 | 11,400 | scarce | unknown | Dragon Tail | 10,434 | 86 | tur_dun01 | 25 | 1 |
| 185 | Raccoon Doll | 12,300 | 24,600 | 27,300 | scarce | unknown | Smokie | 828 | 29 | mjolnir_06 | 70 | 1 |
| 186 | Red Feather | 14,200 | 28,400 | 31,600 | scarce | unknown | Furious Baroness of Retr | 316,630 | 121 | tha_t10 | 2 | 1000 |
| 187 | Ring | 15,800 | 27,000 | 28,500 | scarce | medium | Incubus | 50,856 | 120 | gefenia03 | 21 | 1 |
| 188 | Executioner's Mitten | 17,100 | 34,200 | 37,900 | scarce | unknown | Rybio | 19,878 | 98 | gl_prison | 19 | 2 |
| 189 | Blue Feather | 17,300 | 34,600 | 38,400 | scarce | unknown | Dame of Sentinel Ringlea | 368,440 | 127 | tha_t12 | 2 | 1250 |
| 190 | Transparent Head Protector | 17,400 | 34,800 | 46,500 | scarce | medium | Marine Sphere | 3,662 | 51 | iz_dun03 | 20 | 5 |
| 191 | Fashion Glasses | 22,200 | 44,400 | 49,300 | scarce | unknown | Sage Worm | 4,858 | 70 | gl_cas01 | 17 | 5 |
| 192 | Sword Mace | 26,200 | 45,000 | 47,500 | scarce | low | Dokebi | 5,122 | 68 | pay_dun04 | 40 | 1 |
| 193 | Padded Armor | 27,400 | 43,200 | 45,600 | scarce | none | Rotar Zairo | 2,580 | 48 | prt_fild11 | 50 | 1 |
| 194 | Cruiser Card | 27,400 | 54,800 | 73,200 | scarce | low | Cruiser | 1,842 | 41 | xmas_dun02 | 49 | 1 |
| 195 | Myst Card | 28,700 | 57,400 | 76,500 | scarce | low | Myst | 2,808 | 49 | mjo_dun03 | 39 | 1 |
| 196 | Ora Ora | 28,900 | 57,800 | 31,100 | scarce | unknown | Tarou | 570 | 22 | mjo_dun01 | 63 | 1 |
| 197 | Seyren Windsor Card | 32,900 | 65,800 | 87,800 | scarce | low | Seyren Windsor | 409,924 | 142 | lhz_dun03 | 42 | 1 |
| 198 | Eye of Dullahan | 47,200 | 94,400 | 84,100 | scarce | low | Dullahan | 32,982 | 108 | nif_fild01 | 22 | 1 |
| 199 | Blazer Card | 48,600 | 97,200 | 130,000 | scarce | medium | Blazer | 19,006 | 101 | mag_dun01 | 20 | 1 |
| 200 | Poisonous Toad Card | 49,000 | 98,000 | 131,000 | scarce | low | Poisonous Toad | 11,154 | 87 | ama_dun02 | 35 | 1 |
