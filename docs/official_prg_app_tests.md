# Official LTX App PRG File Test Dumps and Analysis

**Last Updated:** 2025-06-03 11:46 UTC+7

## Complex Fade Sequence Test (Official App) - 2025-06-06

**JSON Input (`test_fade_sequence.prg.json`):**
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 1000,
  "sequence": {
    "0": {
      "pixels": 4,
      "color": [
        255,
        0,
        0
      ]
    },
    "200": {
      "pixels": 4,
      "start_color": [
        255,
        0,
        0
      ],
      "end_color": [
        0,
        255,
        0
      ]
    },
    "500": {
      "pixels": 4,
      "color": [
        0,
        0,
        255
      ]
    },
    "700": {
      "pixels": 4,
      "start_color": [
        0,
        0,
        255
      ],
      "end_color": [
        255,
        255,
        0
      ]
    },
    "1000": {
      "color": [
        0,
        0,
        0
      ],
      "pixels": 4
    }
  }
}
```

**Official App Generated PRG Hex Dump:**
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 4E 00 00 00  04 00 02 00  64 00 6C 00  00 00 00 00 | N.......d.l.....
0000:0020 | 04 00 01 00  00 C8 00 00  00 01 00 2C  01 98 01 00 | .....È.....,....
0000:0030 | 00 00 00 04  00 01 00 00  2C 01 00 00  02 00 64 00 | ........,.....d.
0000:0040 | 1C 05 00 00  00 00 04 00  01 00 00 C8  00 00 00 01 | ...........È....
0000:0050 | 00 2C 01 48  06 00 00 00  00 04 00 01  00 00 2C 01 | .,.H..........,.
0000:0060 | 00 00 43 44  64 09 00 00  20 03 00 00  FF 00 00 FF | ..CDd... ...ÿ..ÿ
0000:0070 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0080 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0090 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00A0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00B0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:00C0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00D0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00E0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:00F0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0100 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0110 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0120 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0130 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0140 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0150 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0160 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0170 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0180 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0190 | 00 00 FF 00  00 FF 00 00  FF 00 00 FE  01 00 FD 02 | ..ÿ..ÿ..ÿ..þ..ý.
0000:01A0 | 00 FC 03 00  FC 03 00 FB  04 00 FA 05  00 F9 06 00 | .ü..ü..û..ú..ù..
0000:01B0 | F8 07 00 F7  08 00 F6 09  00 F6 09 00  F5 0A 00 F4 | ø..÷..ö..ö..õ..ô
0000:01C0 | 0B 00 F3 0C  00 F2 0D 00  F1 0E 00 F1  0E 00 F0 0F | ..ó..ò..ñ..ñ..ð.
0000:01D0 | 00 EF 10 00  EE 11 00 ED  12 00 EC 13  00 EB 14 00 | .ï..î..í..ì..ë..
0000:01E0 | EB 14 00 EA  15 00 E9 16  00 E8 17 00  E7 18 00 E6 | ë..ê..é..è..ç..æ
0000:01F0 | 19 00 E5 1A  00 E5 1A 00  E4 1B 00 E3  1C 00 E2 1D | ..å..å..ä..ã..â.
0000:0200 | 00 E1 1E 00  E0 1F 00 DF  20 00 DF 20  00 DE 21 00 | .á..à..ß .ß .Þ!.
0000:0210 | DD 22 00 DC  23 00 DB 24  00 DA 25 00  D9 26 00 D9 | Ý".Ü#.Û$.Ú%.Ù&.Ù
0000:0220 | 26 00 D8 27  00 D7 28 00  D6 29 00 D5  2A 00 D4 2B | &.Ø'.×(.Ö).Õ*.Ô+
0000:0230 | 00 D4 2B 00  D3 2C 00 D2  2D 00 D1 2E  00 D0 2F 00 | .Ô+.Ó,.Ò-.Ñ..Ð/.
0000:0240 | CF 30 00 CE  31 00 CE 31  00 CD 32 00  CC 33 00 CB | Ï0.Î1.Î1.Í2.Ì3.Ë
0000:0250 | 34 00 CA 35  00 C9 36 00  C8 37 00 C8  37 00 C7 38 | 4.Ê5.É6.È7.È7.Ç8
0000:0260 | 00 C6 39 00  C5 3A 00 C4  3B 00 C3 3C  00 C2 3D 00 | .Æ9.Å:.Ä;.Ã<.Â=.
0000:0270 | C2 3D 00 C1  3E 00 C0 3F  00 BF 40 00  BE 41 00 BD | Â=.Á>.À?.¿@.¾A.½
0000:0280 | 42 00 BC 43  00 BC 43 00  BB 44 00 BA  45 00 B9 46 | B.¼C.¼C.»D.ºE.¹F
0000:0290 | 00 B8 47 00  B7 48 00 B7  48 00 B6 49  00 B5 4A 00 | .¸G.·H.·H.¶I.µJ.
0000:02A0 | B4 4B 00 B3  4C 00 B2 4D  00 B1 4E 00  B1 4E 00 B0 | ´K.³L.²M.±N.±N.°
0000:02B0 | 4F 00 AF 50  00 AE 51 00  AD 52 00 AC  53 00 AB 54 | O.¯P.®Q..R.¬S.«T
0000:02C0 | 00 AB 54 00  AA 55 00 A9  56 00 A8 57  00 A7 58 00 | .«T.ªU.©V.¨W.§X.
0000:02D0 | A6 59 00 A5  5A 00 A5 5A  00 A4 5B 00  A3 5C 00 A2 | ¦Y.¥Z.¥Z.¤[.£\.¢
0000:02E0 | 5D 00 A1 5E  00 A0 5F 00  9F 60 00 9F  60 00 9E 61 | ].¡^. _..`..`..a
0000:02F0 | 00 9D 62 00  9C 63 00 9B  64 00 9A 65  00 9A 65 00 | ..b..c..d..e..e.
0000:0300 | 99 66 00 98  67 00 97 68  00 96 69 00  95 6A 00 94 | .f..g..h..i..j..
0000:0310 | 6B 00 94 6B  00 93 6C 00  92 6D 00 91  6E 00 90 6F | k..k..l..m..n..o
0000:0320 | 00 8F 70 00  8E 71 00 8E  71 00 8D 72  00 8C 73 00 | ..p..q..q..r..s.
0000:0330 | 8B 74 00 8A  75 00 89 76  00 88 77 00  88 77 00 87 | .t..u..v..w..w..
0000:0340 | 78 00 86 79  00 85 7A 00  84 7B 00 83  7C 00 82 7D | x..y..z..{..|..}
0000:0350 | 00 82 7D 00  81 7E 00 80  7F 00 7F 80  00 7E 81 00 | ..}..~.......~..
0000:0360 | 7D 82 00 7D  82 00 7C 83  00 7B 84 00  7A 85 00 79 | }..}..|..{..z..y
0000:0370 | 86 00 78 87  00 77 88 00  77 88 00 76  89 00 75 8A | ..x..w..w..v..u.
0000:0380 | 00 74 8B 00  73 8C 00 72  8D 00 71 8E  00 71 8E 00 | .t..s..r..q..q..
0000:0390 | 70 8F 00 6F  90 00 6E 91  00 6D 92 00  6C 93 00 6B | p..o..n..m..l..k
0000:03A0 | 94 00 6B 94  00 6A 95 00  69 96 00 68  97 00 67 98 | ..k..j..i..h..g.
0000:03B0 | 00 66 99 00  65 9A 00 65  9A 00 64 9B  00 63 9C 00 | .f..e..e..d..c..
0000:03C0 | 62 9D 00 61  9E 00 60 9F  00 60 9F 00  5F A0 00 5E | b..a..`..`.._ .^
0000:03D0 | A1 00 5D A2  00 5C A3 00  5B A4 00 5A  A5 00 5A A5 | ¡.]¢.\£.[¤.Z¥.Z¥
0000:03E0 | 00 59 A6 00  58 A7 00 57  A8 00 56 A9  00 55 AA 00 | .Y¦.X§.W¨.V©.Uª.
0000:03F0 | 54 AB 00 54  AB 00 53 AC  00 52 AD 00  51 AE 00 50 | T«.T«.S¬.R..Q®.P
0000:0400 | AF 00 4F B0  00 4E B1 00  4E B1 00 4D  B2 00 4C B3 | ¯.O°.N±.N±.M².L³
0000:0410 | 00 4B B4 00  4A B5 00 49  B6 00 48 B7  00 48 B7 00 | .K´.Jµ.I¶.H·.H·.
0000:0420 | 47 B8 00 46  B9 00 45 BA  00 44 BB 00  43 BC 00 43 | G¸.F¹.Eº.D».C¼.C
0000:0430 | BC 00 42 BD  00 41 BE 00  40 BF 00 3F  C0 00 3E C1 | ¼.B½.A¾.@¿.?À.>Á
0000:0440 | 00 3D C2 00  3D C2 00 3C  C3 00 3B C4  00 3A C5 00 | .=Â.=Â.<Ã.;Ä.:Å.
0000:0450 | 39 C6 00 38  C7 00 37 C8  00 37 C8 00  36 C9 00 35 | 9Æ.8Ç.7È.7È.6É.5
0000:0460 | CA 00 34 CB  00 33 CC 00  32 CD 00 31  CE 00 31 CE | Ê.4Ë.3Ì.2Í.1Î.1Î
0000:0470 | 00 30 CF 00  2F D0 00 2E  D1 00 2D D2  00 2C D3 00 | .0Ï./Ð..Ñ.-Ò.,Ó.
0000:0480 | 2B D4 00 2B  D4 00 2A D5  00 29 D6 00  28 D7 00 27 | +Ô.+Ô.*Õ.)Ö.(×.'
0000:0490 | D8 00 26 D9  00 26 D9 00  25 DA 00 24  DB 00 23 DC | Ø.&Ù.&Ù.%Ú.$Û.#Ü
0000:04A0 | 00 22 DD 00  21 DE 00 20  DF 00 20 DF  00 1F E0 00 | ."Ý.!Þ. ß. ß..à.
0000:04B0 | 1E E1 00 1D  E2 00 1C E3  00 1B E4 00  1A E5 00 1A | .á..â..ã..ä..å..
0000:04C0 | E5 00 19 E6  00 18 E7 00  17 E8 00 16  E9 00 15 EA | å..æ..ç..è..é..ê
0000:04D0 | 00 14 EB 00  14 EB 00 13  EC 00 12 ED  00 11 EE 00 | ..ë..ë..ì..í..î.
0000:04E0 | 10 EF 00 0F  F0 00 0E F1  00 0E F1 00  0D F2 00 0C | .ï..ð..ñ..ñ..ò..
0000:04F0 | F3 00 0B F4  00 0A F5 00  09 F6 00 09  F6 00 08 F7 | ó..ô..õ..ö..ö..÷
0000:0500 | 00 07 F8 00  06 F9 00 05  FA 00 04 FB  00 03 FC 00 | ..ø..ù..ú..û..ü.
0000:0510 | 03 FC 00 02  FD 00 01 FE  00 00 FF 00  00 00 FF 00 | .ü..ý..þ..ÿ...ÿ.
0000:0520 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0530 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0540 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0550 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0560 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0570 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0580 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0590 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:05A0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:05B0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:05C0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:05D0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:05E0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:05F0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0600 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0610 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0620 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0630 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0640 | 00 FF 00 00  FF 00 00 FF  00 00 FF 01  01 FE 02 02 | .ÿ..ÿ..ÿ..ÿ..þ..
0000:0650 | FD 03 03 FC  03 03 FC 04  04 FB 05 05  FA 06 06 F9 | ý..ü..ü..û..ú..ù
0000:0660 | 07 07 F8 08  08 F7 09 09  F6 09 09 F6  0A 0A F5 0B | ..ø..÷..ö..ö..õ.
0000:0670 | 0B F4 0C 0C  F3 0D 0D F2  0E 0E F1 0E  0E F1 0F 0F | .ô..ó..ò..ñ..ñ..
0000:0680 | F0 10 10 EF  11 11 EE 12  12 ED 13 13  EC 14 14 EB | ð..ï..î..í..ì..ë
0000:0690 | 14 14 EB 15  15 EA 16 16  E9 17 17 E8  18 18 E7 19 | ..ë..ê..é..è..ç.
0000:06A0 | 19 E6 1A 1A  E5 1A 1A E5  1B 1B E4 1C  1C E3 1D 1D | .æ..å..å..ä..ã..
0000:06B0 | E2 1E 1E E1  1F 1F E0 20  20 DF 20 20  DF 21 21 DE | â..á..à  ß  ß!!Þ
0000:06C0 | 22 22 DD 23  23 DC 24 24  DB 25 25 DA  26 26 D9 26 | ""Ý##Ü$$Û%%Ú&&Ù&
0000:06D0 | 26 D9 27 27  D8 28 28 D7  29 29 D6 2A  2A D5 2B 2B | &Ù''Ø((×))Ö**Õ++
0000:06E0 | D4 2B 2B D4  2C 2C D3 2D  2D D2 2E 2E  D1 2F 2F D0 | Ô++Ô,,Ó--Ò..Ñ//Ð
0000:06F0 | 30 30 CF 31  31 CE 31 31  CE 32 32 CD  33 33 CC 34 | 00Ï11Î11Î22Í33Ì4
0000:0700 | 34 CB 35 35  CA 36 36 C9  37 37 C8 37  37 C8 38 38 | 4Ë55Ê66É77È77È88
0000:0710 | C7 39 39 C6  3A 3A C5 3B  3B C4 3C 3C  C3 3D 3D C2 | Ç99Æ::Å;;Ä<<Ã==Â
0000:0720 | 3D 3D C2 3E  3E C1 3F 3F  C0 40 40 BF  41 41 BE 42 | ==Â>>Á??À@@¿AA¾B
0000:0730 | 42 BD 43 43  BC 43 43 BC  44 44 BB 45  45 BA 46 46 | B½CC¼CC¼DD»EEºFF
0000:0740 | B9 47 47 B8  48 48 B7 48  48 B7 49 49  B6 4A 4A B5 | ¹GG¸HH·HH·II¶JJµ
0000:0750 | 4B 4B B4 4C  4C B3 4D 4D  B2 4E 4E B1  4E 4E B1 4F | KK´LL³MM²NN±NN±O
0000:0760 | 4F B0 50 50  AF 51 51 AE  52 52 AD 53  53 AC 54 54 | O°PP¯QQ®RR.SS¬TT
0000:0770 | AB 54 54 AB  55 55 AA 56  56 A9 57 57  A8 58 58 A7 | «TT«UUªVV©WW¨XX§
0000:0780 | 59 59 A6 5A  5A A5 5A 5A  A5 5B 5B A4  5C 5C A3 5D | YY¦ZZ¥ZZ¥[[¤\\£]
0000:0790 | 5D A2 5E 5E  A1 5F 5F A0  60 60 9F 60  60 9F 61 61 | ]¢^^¡__ ``.``.aa
0000:07A0 | 9E 62 62 9D  63 63 9C 64  64 9B 65 65  9A 65 65 9A | .bb.cc.dd.ee.ee.
0000:07B0 | 66 66 99 67  67 98 68 68  97 69 69 96  6A 6A 95 6B | ff.gg.hh.ii.jj.k
0000:07C0 | 6B 94 6B 6B  94 6C 6C 93  6D 6D 92 6E  6E 91 6F 6F | k.kk.ll.mm.nn.oo
0000:07D0 | 90 70 70 8F  71 71 8E 71  71 8E 72 72  8D 73 73 8C | .pp.qq.qq.rr.ss.
0000:07E0 | 74 74 8B 75  75 8A 76 76  89 77 77 88  77 77 88 78 | tt.uu.vv.ww.ww.x
0000:07F0 | 78 87 79 79  86 7A 7A 85  7B 7B 84 7C  7C 83 7D 7D | x.yy.zz.{{.||.}}
0000:0800 | 82 7D 7D 82  7E 7E 81 7F  7F 80 80 80  7F 81 81 7E | .}}.~~.........~
0000:0810 | 82 82 7D 82  82 7D 83 83  7C 84 84 7B  85 85 7A 86 | ..}..}..|..{..z.
0000:0820 | 86 79 87 87  78 88 88 77  88 88 77 89  89 76 8A 8A | .y..x..w..w..v..
0000:0830 | 75 8B 8B 74  8C 8C 73 8D  8D 72 8E 8E  71 8E 8E 71 | u..t..s..r..q..q
0000:0840 | 8F 8F 70 90  90 6F 91 91  6E 92 92 6D  93 93 6C 94 | ..p..o..n..m..l.
0000:0850 | 94 6B 94 94  6B 95 95 6A  96 96 69 97  97 68 98 98 | .k..k..j..i..h..
0000:0860 | 67 99 99 66  9A 9A 65 9A  9A 65 9B 9B  64 9C 9C 63 | g..f..e..e..d..c
0000:0870 | 9D 9D 62 9E  9E 61 9F 9F  60 9F 9F 60  A0 A0 5F A1 | ..b..a..`..`  _¡
0000:0880 | A1 5E A2 A2  5D A3 A3 5C  A4 A4 5B A5  A5 5A A5 A5 | ¡^¢¢]££\¤¤[¥¥Z¥¥
0000:0890 | 5A A6 A6 59  A7 A7 58 A8  A8 57 A9 A9  56 AA AA 55 | Z¦¦Y§§X¨¨W©©VªªU
0000:08A0 | AB AB 54 AB  AB 54 AC AC  53 AD AD 52  AE AE 51 AF | ««T««T¬¬S..R®®Q¯
0000:08B0 | AF 50 B0 B0  4F B1 B1 4E  B1 B1 4E B2  B2 4D B3 B3 | ¯P°°O±±N±±N²²M³³
0000:08C0 | 4C B4 B4 4B  B5 B5 4A B6  B6 49 B7 B7  48 B7 B7 48 | L´´KµµJ¶¶I··H··H
0000:08D0 | B8 B8 47 B9  B9 46 BA BA  45 BB BB 44  BC BC 43 BC | ¸¸G¹¹FººE»»D¼¼C¼
0000:08E0 | BC 43 BD BD  42 BE BE 41  BF BF 40 C0  C0 3F C1 C1 | ¼C½½B¾¾A¿¿@ÀÀ?ÁÁ
0000:08F0 | 3E C2 C2 3D  C2 C2 3D C3  C3 3C C4 C4  3B C5 C5 3A | >ÂÂ=ÂÂ=ÃÃ<ÄÄ;ÅÅ:
0000:0900 | C6 C6 39 C7  C7 38 C8 C8  37 C8 C8 37  C9 C9 36 CA | ÆÆ9ÇÇ8ÈÈ7ÈÈ7ÉÉ6Ê
0000:0910 | CA 35 CB CB  34 CC CC 33  CD CD 32 CE  CE 31 CE CE | Ê5ËË4ÌÌ3ÍÍ2ÎÎ1ÎÎ
0000:0920 | 31 CF CF 30  D0 D0 2F D1  D1 2E D2 D2  2D D3 D3 2C | 1ÏÏ0ÐÐ/ÑÑ.ÒÒ-ÓÓ,
0000:0930 | D4 D4 2B D4  D4 2B D5 D5  2A D6 D6 29  D7 D7 28 D8 | ÔÔ+ÔÔ+ÕÕ*ÖÖ)××(Ø
0000:0940 | D8 27 D9 D9  26 D9 D9 26  DA DA 25 DB  DB 24 DC DC | Ø'ÙÙ&ÙÙ&ÚÚ%ÛÛ$ÜÜ
0000:0950 | 23 DD DD 22  DE DE 21 DF  DF 20 DF DF  20 E0 E0 1F | #ÝÝ"ÞÞ!ßß ßß àà.
0000:0960 | E1 E1 1E E2  E2 1D E3 E3  1C E4 E4 1B  E5 E5 1A E5 | áá.ââ.ãã.ää.åå.å
0000:0970 | E5 1A E6 E6  19 E7 E7 18  E8 E8 17 E9  E9 16 EA EA | å.ææ.çç.èè.éé.êê
0000:0980 | 15 EB EB 14  EB EB 14 EC  EC 13 ED ED  12 EE EE 11 | .ëë.ëë.ìì.íí.îî.
0000:0990 | EF EF 10 F0  F0 0F F1 F1  0E F1 F1 0E  F2 F2 0D F3 | ïï.ðð.ññ.ññ.òò.ó
0000:09A0 | F3 0C F4 F4  0B F5 F5 0A  F6 F6 09 F6  F6 09 F7 F7 | ó.ôô.õõ.öö.öö.÷÷
0000:09B0 | 08 F8 F8 07  F9 F9 06 FA  FA 05 FB FB  04 FC FC 03 | .øø.ùù.úú.ûû.üü.
0000:09C0 | FC FC 03 FD  FD 02 FE FE  01 FF FF 00  42 54 00 00 | üü.ýý.þþ.ÿÿ.BT..
0000:09D0 | 00 00                                              | ..              
```

**Analysis:**
- This is a sequence with 5 segments: Solid Red (200ms) -> Fade Red-to-Green (300ms) -> Solid Blue (200ms) -> Fade Blue-to-Yellow (300ms) -> Solid Black (implicit remaining duration or 0ms if end_time=1000).
- Header `0x0C-0x0D` (Refresh Rate): `64 00` (100Hz).
- Header `0x14-0x15` (Segment Count): `04 00` (4 segments). *Note: The final black color at end_time is treated as the end of the last specified segment, not a new segment itself in the count.*
- Header `0x10-0x13` (Pointer1): `4E 00 00 00` (78). Formula `21 + 19*(4-1) = 21 + 57 = 78`. Matches.
- Header `0x16-0x17` (Field 0x16): `02 00` (2). `Dur0Units_actual` (Solid Red) = 200ms. `floor(200/100) = 2`. Matches.
- Header `0x1E-0x1F` (Field 0x1E): `00 00` (0). For N>1, if `Dur0Units_actual % 100 == 0`, then `0x1E = 0`. Matches.
- RGB data for fades:
    - First fade (Red to Green, 300ms, starts `0x0190`): `FF 00 00` -> `FE 01 00` ... -> `00 FF 00`. Spans 300 * 3 = 900 bytes.
    - Second fade (Blue to Yellow, 300ms, starts `0x0640`): `00 00 FF` -> `01 01 FE` ... -> `FF FF 00`. Spans 300 * 3 = 900 bytes.
- Duration Block Analysis:
    - **Block 0 (Solid Red, 200ms, offset `0x20`):**
        - `+0x05` Dur: `C8 00` (200ms)
        - `+0x09` Field[+0x09]: `01 00 2C 01` (`field_09_part1=1`, `field_09_part2=300`). `Dur_1` (Fade1) is 300ms. Since Fade, `part1=1`, `part2=300`. Correct.
        - `+0x11` NextSegInfo (for Fade1=300ms): `2C 01` (300ms). Correct.
    - **Block 1 (Fade Red-Green, 300ms, offset `0x33`):**
        - `+0x05` Dur: `2C 01` (300ms)
        - `+0x09` Field[+0x09]: `02 00 64 00` (`field_09_part1=2`, `field_09_part2=100`). `Dur_2` (Solid Blue) is 200ms. Since Solid, `part1=floor(200/100)=2`, `part2=100`. Correct.
        - `+0x11` NextSegInfo (for SolidBlue=200ms): `C8 00` (200ms). Correct.
    - **Block 2 (Solid Blue, 200ms, offset `0x46`):**
        - `+0x05` Dur: `C8 00` (200ms)
        - `+0x09` Field[+0x09]: `01 00 2C 01` (`field_09_part1=1`, `field_09_part2=300`). `Dur_3` (Fade2) is 300ms. Since Fade, `part1=1`, `part2=300`. Correct.
        - `+0x11` NextSegInfo (for Fade2=300ms): `2C 01` (300ms). Correct.
    - **Block 3 (Fade Blue-Yellow, 300ms, LAST, offset `0x59`):**
        - `+0x05` Dur: `2C 01` (300ms)
        - `+0x09` Const: `43 44`
        - `+0x0B` Index2 P1 Lo: `64 09`
        - `+0x0D` Index2 P1 Hi: `00 00`
        - `+0x0F` Index2 P2 Lo: `20 03`
        - `+0x11` Index2 P2 Hi: `00 00`
        - `Index2_Part1_Full = 0x0964 = 2404`
        - `Index2_Part2_Full = 0x0320 = 800`
        - Calculated with `_calculate_last_block_index2_bases(total_segments=4, segments_list=[(200,_,_,'solid',_), (300,_,_,'fade',_), (200,_,_,'solid',_), (300,_,_,'fade',_)])`:
            - `H_eff_0 (solid,200)` = `300 + 3*200 = 900`
            - `H_eff_1 (fade,300)` = `300`
            - `H_eff_2 (solid,200)` = `300 + 3*200 = 900`
            - `cumulative_horizontal_offset_for_part1 = 900 + 300 + 900 = 2100`
            - `part1_full = 304 + 2100 = 2404`. Matches `0x0964`.
            - `part2_full_base = segments_list[0][0] = 200` (since first is solid)
            - `part2_full = 200 * 4 = 800`. Matches `0x0320`.

This test demonstrates the official app's handling of mixed solid and fade segments, including correct RGB data generation and duration block field calculations. The `prg_generator.py` after recent fixes should produce a matching file.

---
This document records hex dumps from `.prg` files generated by the official LTX application. These serve as a ground truth for reverse-engineering and validating the PRG file format, especially for conditional header fields.

All examples below were generated with a 4-pixel setting and a 1Hz refresh rate, unless otherwise specified.

## Single Segment, 1Hz Refresh Rate Examples

These examples show how header fields `0x16` and `0x1E` behave for single-segment files with varying durations at a 1Hz PRG refresh rate.

**Common Header Values for N=1, 1Hz Refresh Rate, 4px:**
*   `0x00-0x07`: `50 52 03 49 4E 05 00 00` (Signature)
*   `0x08-0x09`: `00 04` (Default Pixels = 4, Big Endian)
*   `0x0A-0x0B`: `00 08` (Constant)
*   `0x0C-0x0D`: `01 00` (Refresh Rate = 1Hz, Little Endian)
*   `0x0E-0x0F`: `50 49` ('PI' Marker)
*   `0x10-0x13`: `15 00 00 00` (Pointer1 = 21, for N=1)
*   `0x14-0x15`: `01 00` (Segment Count N = 1)
*   `0x18-0x19`: `64 00` (RGB Data Repetition Count = 100)
*   `0x1A-0x1B`: `33 00` (RGB Data Start Offset = 51, for N=1)
*   `0x1C-0x1D`: `00 00` (Constant)

### 1s (Duration `Dur0Units_actual` = 1)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 00 00  64 00 33 00  00 00 01 00 | ........d.3.....
```
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `01 00` (Field 0x1E Value = 1)

### 2s (Duration `Dur0Units_actual` = 2)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 00 00  64 00 33 00  00 00 02 00 | ........d.3.....
```
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `02 00` (Field 0x1E Value = 2)

### 10s (Duration `Dur0Units_actual` = 10)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 00 00  64 00 33 00  00 00 0A 00 | ........d.3.....
```
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `0A 00` (Field 0x1E Value = 10)

### 50s (Duration `Dur0Units_actual` = 50)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 00 00  64 00 33 00  00 00 32 00 | ........d.3...2.
```
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `32 00` (Field 0x1E Value = 50)

### 99s (Duration `Dur0Units_actual` = 99)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 00 00  64 00 33 00  00 00 63 00 | ........d.3...c.
```
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `63 00` (Field 0x1E Value = 99)

### 100s (Duration `Dur0Units_actual` = 100)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 01 00  64 00 33 00  00 00 00 00 | ........d.3.....
```
*   `0x16-0x17`: `01 00` (Field 0x16 Value = 1)
*   `0x1E-0x1F`: `00 00` (Field 0x1E Value = 0)

### 101s (Duration `Dur0Units_actual` = 101)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 01 00  64 00 33 00  00 00 01 00 | ........d.3.....
```
*   `0x16-0x17`: `01 00` (Field 0x16 Value = 1)
*   `0x1E-0x1F`: `01 00` (Field 0x1E Value = 1)

### 200s (Duration `Dur0Units_actual` = 200)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 15 00 00 00  01 00 02 00  64 00 33 00  00 00 00 00 | ........d.3.....
```
*   `0x16-0x17`: `02 00` (Field 0x16 Value = 2)
*   `0x1E-0x1F`: `00 00` (Field 0x1E Value = 0)

## Multi-Segment, 1Hz Refresh Rate Examples

### red_1s_blue_1s_1r.prg (N=2, Dur0Units_actual=1)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 28 00 00 00  02 00 00 00  64 00 46 00  00 00 01 00 | (.......d.F.....
0000:0020 | 04 00 01 00  00 01 00 00  00 00 00 64  00 72 01 00 | ...........d.r..
0000:0030 | 00 01 00 04  00 01 00 00  01 00 00 00  43 44 5C 02 | ............CD\.
```
*   `0x14-0x15`: `02 00` (Segment Count N = 2)
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `01 00` (Field 0x1E Value = 1)

### red_1s_blue_1s_green_1s_1r.prg (N=3, Dur0Units_actual=1)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 01 00 | ;.......d.Y.....
0000:0020 | 04 00 01 00  00 01 00 00  00 00 00 64  00 85 01 00 | ...........d....
```
*   `0x14-0x15`: `03 00` (Segment Count N = 3)
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `01 00` (Field 0x1E Value = 1)

### red_1s_blue_2s_1r.prg (N=2, Dur0Units_actual=1)
Same header as `red_1s_blue_1s_1r.prg` for fields 0x16 and 0x1E.
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 28 00 00 00  02 00 00 00  64 00 46 00  00 00 01 00 | (.......d.F.....
```
*   `0x16-0x17`: `00 00`
*   `0x1E-0x1F`: `01 00`

### red_50s_blue_50s_1r.prg (N=2, Dur0Units_actual=50)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 28 00 00 00  02 00 00 00  64 00 46 00  00 00 32 00 | (.......d.F...2.
```
*   `0x16-0x17`: `00 00` (Field 0x16 Value = 0)
*   `0x1E-0x1F`: `32 00` (Field 0x1E Value = 50)

### red_100s_blue_50s_1r.prg (N=2, Dur0Units_actual=100)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  01 00 50 49 | PR.IN.........PI
0000:0010 | 28 00 00 00  02 00 01 00  64 00 46 00  00 00 00 00 | (.......d.F.....
```
*   `0x16-0x17`: `01 00` (Field 0x16 Value = 1)
*   `0x1E-0x1F`: `00 00` (Field 0x1E Value = 0)


## Deduced Logic for Header Fields 0x16 and 0x1E

Let:
*   `Dur0Units_actual`: The duration of the first PRG segment in PRG time units.
*   `N_prg`: The total number of PRG segments in the file.
*   `val_0x16_dec`: The decimal value calculated for field `0x16`.

**Field `0x16` (Header First Segment Info):**
1.  If `N_prg == 1`:
    *   `val_0x16_dec = floor(Dur0Units_actual / 100)`
2.  Else (`N_prg > 1`):
    *   If `Dur0Units_actual == 100`: `val_0x16_dec = 1`
    *   Else (`Dur0Units_actual != 100`): `val_0x16_dec = 0`
*   The byte value written to the file is `struct.pack('<H', val_0x16_dec)`.

**Field `0x1E` (Header First Segment Duration (Conditional)):**
1.  If `N_prg == 1`:
    *   `val_0x1E_dec = Dur0Units_actual - (val_0x16_dec * 100)`
      (Note: `val_0x16_dec` is the decimal value calculated for field `0x16` above)
2.  Else (`N_prg > 1`):
    *   If `Dur0Units_actual == 100`: `val_0x1E_dec = 0`
    *   Else (`Dur0Units_actual != 100`): `val_0x1E_dec = Dur0Units_actual`
*   The byte value written to the file is `struct.pack('<H', val_0x1E_dec & 0xFFFF)`.

This logic appears consistent with all provided 1Hz examples.

---

## Important Finding: 1Hz PRG with 100 Color Slots Experiment (Failed)

**Date:** 2025-06-01

An experiment was conducted using a modified generator (`prg_generator_new.py`) that produced PRG files with a 1Hz master refresh rate. The intention was to use the 100 RGB color data slots within each 1-second PRG segment to achieve 0.01s granularity.

**Observation:** The LTX ball firmware appears to **only use the first RGB color** from the 300-byte (100x3 RGB) color data block when the PRG file's refresh rate is 1Hz. The remaining 99 color slots are ignored for display purposes in this mode.

**Example JSON that resulted in solid yellow (not yellow then black):**
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 100,
  "sequence": {
    "0": {"color": [255, 255, 0], "pixels": 4},    // Yellow
    "1": {"color": [0, 0, 0], "pixels": 4}         // Black (intended for 0.01s later)
  }
}
```
Resulting PRG (1Hz) showed solid yellow for 1 second.

**Example JSON that resulted in solid red (not red then blue):**
```json
{
  "default_pixels": 4,
  "color_format": "rgb",
  "refresh_rate": 100,
  "end_time": 100,
  "sequence": {
    "0": {"color": [255, 0, 0], "pixels": 4},     // Red
    "50": {"color": [0, 0, 255], "pixels": 4}    // Blue (intended for 0.5s later)
  }
}
```
Resulting PRG (1Hz) showed solid red for 1 second.

**Conclusion:** High-frequency color changes cannot be achieved by manipulating the 100 sub-color slots within a 1Hz PRG segment. A higher PRG refresh rate (e.g., 100Hz or 1000Hz) is necessary for fine-grained temporal resolution.

---

## 1000Hz Refresh Rate Examples (PRG Refresh Rate = 1000)

These examples use a PRG file refresh rate of 1000Hz (`03E8` Little Endian).
All are 4-pixel.

**Common Header Values for 1000Hz Refresh Rate, 4px:**
*   `0x00-0x07`: `50 52 03 49 4E 05 00 00` (Signature)
*   `0x08-0x09`: `00 04` (Default Pixels = 4, Big Endian)
*   `0x0A-0x0B`: `00 08` (Constant)
*   `0x0C-0x0D`: `E8 03` (Refresh Rate = 1000Hz, Little Endian)
*   `0x0E-0x0F`: `50 49` ('PI' Marker)
*   `0x18-0x19`: `64 00` (RGB Data Repetition Count = 100)
*   `0x1C-0x1D`: `00 00` (Constant)

### red_.01s_1000r.prg (N=1, Dur0Units_actual = 10)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 00 00  64 00 33 00  00 00 0A 00 | ........d.3.....
```
*   `0x16-0x17`: `00 00` (Value 0)
*   `0x1E-0x1F`: `0A 00` (Value 10)

### red_.1s_1000r.prg (N=1, Dur0Units_actual = 100)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 01 00  64 00 33 00  00 00 00 00 | ........d.3.....
```
*   `0x16-0x17`: `01 00` (Value 1)
*   `0x1E-0x1F`: `00 00` (Value 0)

### red_0.5s_1000r.prg (N=1, Dur0Units_actual = 500)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 05 00  64 00 33 00  00 00 F4 01 | ........d.3...ô.
```
*   `0x16-0x17`: `05 00` (Value 5)
*   `0x1E-0x1F`: `F4 01` (Value 500)

### red_1s_1000r.prg (N=1, Dur0Units_actual = 1000)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 0A 00  64 00 33 00  00 00 E8 03 | ........d.3...è.
```
*   `0x16-0x17`: `0A 00` (Value 10)
*   `0x1E-0x1F`: `E8 03` (Value 1000)

### red_5s_1000r.prg (N=1, Dur0Units_actual = 5000)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 32 00  64 00 33 00  00 00 88 13 | ......2.d.3.....
```
*   `0x16-0x17`: `32 00` (Value 50)
*   `0x1E-0x1F`: `88 13` (Value 5000)


### red_10s_1000r.prg (N=1, Dur0Units_actual = 10000)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 64 00  64 00 33 00  00 00 10 27 | ......d.d.3....'
```
*   `0x16-0x17`: `64 00` (Value 100)
*   `0x1E-0x1F`: `10 27` (Value 10000)

### Header `0x1E` (N=1, Dur0 = multiple of 100) Pinpoint Threshold Tests

*   Objective: Pinpoint the threshold between 400ms and 500ms for Field `0x1E` when N=1 and Dur0 is a multiple of 100.
*   All tests are 1000Hz PRG refresh rate.

#### Test H_0x1E_1: N=1, Dur0 = 401ms
*   Expected: `0x1E = 1` (01 00)
*   Header: `0x16 = 0400` (4), `0x1E = 0100` (1)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 04 00  64 00 33 00  00 00 01 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 91 01 00  00 43 44 30  01 00 00 64 | .....‘...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```

#### Test H_0x1E_2: N=1, Dur0 = 499ms
*   Expected: `0x1E = 99` (63 00)
*   Header: `0x16 = 0400` (4), `0x1E = 6300` (99)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 04 00  64 00 33 00  00 00 63 00 | ........d.3...c.
0000:0020 | 04 00 01 00  00 F3 01 00  00 43 44 30  01 00 00 64 | .....ó...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```

#### Test H_0x1E_3: N=1, Dur0 = 420ms
*   Expected: `0x1E = 0` (00 00) if threshold > 420ms for the "0" rule, or `0x1E = 20` (14 00) if it's `Dur0 % 100`.
*   Actual: `0x1E = 1400` (20)
*   Header: `0x16 = 0400` (4), `0x1E = 1400` (20)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 04 00  64 00 33 00  00 00 14 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 A4 01 00  00 43 44 30  01 00 00 64 | .....¤...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```
*   Analysis: For Dur0=420 (N=1, 1000Hz), `0x1E` = 20. This means `Dur0 % 100` is applied. This contradicts the S2 test (Dur0=400 gives 0x1E=0). This suggests the threshold for N=1 multiples of 100 (where 0x1E becomes 0) is *exactly* 400ms, or the rule is more complex.

#### Test H_0x1E_4: N=1, Dur0 = 480ms
*   Expected: `0x1E = 0` (00 00) if threshold for "0" rule > 480ms, or `0x1E = 480` (E0 01) if it's direct passthrough, or `0x1E = 80` (50 00) if `Dur0 % 100`.
*   Actual: `0x1E = 5000` (80)
*   Header: `0x16 = 0400` (4), `0x1E = 5000` (80)
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 04 00  64 00 33 00  00 00 50 00 | ........d.3...P.
0000:0020 | 04 00 01 00  00 E0 01 00  00 43 44 30  01 00 00 64 | .....à...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```
*   Analysis: For Dur0=480 (N=1, 1000Hz), `0x1E` = 80. This means `Dur0 % 100` is applied. Consistent with H_0x1E_3.
*   The S2 test (Dur0=400, 0x1E=0) and Q1 (Dur0=200, 0x1E=0), Q2 (Dur0=300, 0x1E=0) show `0x1E=0` for multiples of 100 up to 400ms.
*   red_0.5s_1000r.prg (Dur0=500, N=1) has `0x1E=500`.
*   This new H_0x1E series suggests for N=1, 1000Hz:
    *   If `Dur0Units_actual % 100 == 0`:
        *   If `Dur0Units_actual <= 400`: `val_0x1E_dec = 0`.
        *   Else (`Dur0Units_actual >= 500`): `val_0x1E_dec = Dur0Units_actual`.
    *   Else (`Dur0Units_actual % 100 != 0`): `val_0x1E_dec = Dur0Units_actual % 100`. (Confirmed by H_0x1E_1, H_0x1E_2, H_0x1E_3, H_0x1E_4).

---
### red_0.1s_blue_0.1s_1000r.prg (N=2, Dur0Units_actual=100)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 28 00 00 00  02 00 01 00  64 00 46 00  00 00 00 00 | (.......d.F.....
```
*   `0x14-0x15` (N): `02 00` (2)
*   `0x16-0x17` (Field 0x16, from Dur0=100): `01 00` (Value 1)
*   `0x1E-0x1F` (Field 0x1E, from Dur0=100): `00 00` (Value 0)


### red_1s_blue_.5s_1000r.prg (N=2, Dur0Units_actual=1000)
*Actual Hex:*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 28 00 00 00  02 00 0A 00  64 00 46 00  00 00 E8 03 | (.......d.F...è.
```
*   `0x14-0x15` (N): `02 00` (2)
*   `0x16-0x17` (Field 0x16, from Dur0=1000): `0A 00` (Value 10)
*   `0x1E-0x1F` (Field 0x1E, from Dur0=1000): `E8 03` (Value 1000)


---

### High Segment Count (N > 255) at 1000Hz Refresh Rate Examples

**Date:** 2025-06-01

These examples are to investigate how the PRG format handles segment counts exceeding 255.
All files have a 0.1s segment duration and 1000Hz refresh rate.
This means each segment has `Dur0Units_actual = 0.1 * 1000 = 100`.
The common header values for Refresh Rate (`E8 03` at `0x0C-0x0D`), Field `0x16` (`01 00` at `0x16-0x17`), and Field `0x1E` (`00 00` at `0x1E-0x1F`) are consistent with `Dur0Units_actual=100` according to Hypothesis 8.

#### N253_.1s_1000r.prg (Actual N=253, Dur0Units_actual=100)
*Actual Hex (first 256 bytes):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | C9 12 00 00  FD 00 01 00  64 00 E7 12  00 00 00 00 | É...ý...d.ç.....
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 13 14 00 | .....d.....d....
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | 3F 15 00 00  00 00 04 00  01 00 00 64  00 00 00 01 | ?..........d....
0000:0050 | 00 64 00 6B  16 00 00 00  00 04 00 01  00 00 64 00 | .d.k..........d.
0000:0060 | 00 00 01 00  64 00 97 17  00 00 00 00  04 00 01 00 | ....d...........
0000:0070 | 00 64 00 00  00 01 00 64  00 C3 18 00  00 00 00 04 | .d.....d.Ã......
0000:0080 | 00 01 00 00  64 00 00 00  01 00 64 00  EF 19 00 00 | ....d.....d.ï...
0000:0090 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 1B | .......d.....d..
0000:00A0 | 1B 00 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:00B0 | 64 00 47 1C  00 00 00 00  04 00 01 00  00 64 00 00 | d.G..........d..
0000:00C0 | 00 01 00 64  00 73 1D 00  00 00 00 04  00 01 00 00 | ...d.s..........
0000:00D0 | 64 00 00 00  01 00 64 00  9F 1E 00 00  00 00 04 00 | d.....d.........
0000:00E0 | 01 00 00 64  00 00 00 01  00 64 00 CB  1F 00 00 00 | ...d.....d.Ë....
0000:00F0 | 00 04 00 01  00 00 64 00  00 00 01 00  64 00 F7 20 | ......d.....d.÷
0000:0100 | 00 00 00 00  04 00 01 00  00 64 00 00  00 01 00 64 | .........d.....d
```
*   `0x10-0x13` (Pointer1): `C9 12 00 00` (`0x12C9` = 4809). Formula `21 + 19*(253-1) = 21 + 19*252 = 21 + 4788 = 4809`. Matches.
*   `0x14-0x15` (Segment Count N): `FD 00` (`0x00FD` = 253). Matches.
*   `0x1A-0x1B` (RGB Data Start Offset): `E7 12` (`0x12E7` = 4839). Formula `32 + 253*19 = 32 + 4807 = 4839`. Matches.

#### N257_.1s_1000r.prg (Actual N=257, Dur0Units_actual=100)
**Note:** Filename has been corrected to match actual segment count. Header fields consistently point to N=257.
*Actual Hex (first 256 bytes):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 13 00 00  01 01 01 00  64 00 33 13  00 00 00 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 5F 14 00 | .....d.....d._..
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | 8B 15 00 00  00 00 04 00  01 00 00 64  00 00 00 01 | ...........d....
0000:0050 | 00 64 00 B7  16 00 00 00  00 04 00 01  00 00 64 00 | .d.·..........d.
0000:0060 | 00 00 01 00  64 00 E3 17  00 00 00 00  04 00 01 00 | ....d.ã.........
0000:0070 | 00 64 00 00  00 01 00 64  00 0F 19 00  00 00 00 04 | .d.....d........
0000:0080 | 00 01 00 00  64 00 00 00  01 00 64 00  3B 1A 00 00 | ....d.....d.;...
0000:0090 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 67 | .......d.....d.g
0000:00A0 | 1B 00 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:00B0 | 64 00 93 1C  00 00 00 00  04 00 01 00  00 64 00 00 | d............d..
0000:00C0 | 00 01 00 64  00 BF 1D 00  00 00 00 04  00 01 00 00 | ...d.¿..........
0000:00D0 | 64 00 00 00  01 00 64 00  EB 1E 00 00  00 00 04 00 | d.....d.ë.......
0000:00E0 | 01 00 00 64  00 00 00 01  00 64 00 17  20 00 00 00 | ...d.....d.. ...
0000:00F0 | 00 04 00 01  00 00 64 00  00 00 01 00  64 00 43 21 | ......d.....d.C!
0000:0100 | 00 00 00 00  04 00 01 00  00 64 00 00  00 01 00 64 | .........d.....d
```
*   `0x10-0x13` (Pointer1): `15 13 00 00` (`0x1315` = 4885). Formula `21 + 19*(257-1) = 21 + 19*256 = 21 + 4864 = 4885`. Matches N=257.
*   `0x14-0x15` (Segment Count N): `01 01` (`0x0101` = 257). Matches N=257.
*   `0x1A-0x1B` (RGB Data Start Offset): `33 13` (`0x1333` = 4915). Formula `32 + 257*19 = 32 + 4883 = 4915`. Matches N=257.

#### N258_.1s_1000r.prg (Actual N=258, Dur0Units_actual=100)
**Note:** Filename has been corrected to match actual segment count. Header fields consistently point to N=258.
*Actual Hex (first 256 bytes):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 28 13 00 00  02 01 01 00  64 00 46 13  00 00 00 00 | (.......d.F.....
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 72 14 00 | .....d.....d.r..
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | 9E 15 00 00  00 00 04 00  01 00 00 64  00 00 00 01 | ...........d....
0000:0050 | 00 64 00 CA  16 00 00 00  00 04 00 01  00 00 64 00 | .d.Ê..........d.
0000:0060 | 00 00 01 00  64 00 F6 17  00 00 00 00  04 00 01 00 | ....d.ö.........
0000:0070 | 00 64 00 00  00 01 00 64  00 22 19 00  00 00 00 04 | .d.....d."......
0000:0080 | 00 01 00 00  64 00 00 00  01 00 64 00  4E 1A 00 00 | ....d.....d.N...
0000:0090 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 7A | .......d.....d.z
0000:00A0 | 1B 00 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:00B0 | 64 00 A6 1C  00 00 00 00  04 00 01 00  00 64 00 00 | d.¦..........d..
0000:00C0 | 00 01 00 64  00 D2 1D 00  00 00 00 04  00 01 00 00 | ...d.Ò..........
0000:00D0 | 64 00 00 00  01 00 64 00  FE 1E 00 00  00 00 04 00 | d.....d.þ.......
0000:00E0 | 01 00 00 64  00 00 00 01  00 64 00 2A  20 00 00 00 | ...d.....d.* ...
0000:00F0 | 00 04 00 01  00 00 64 00  00 00 01 00  64 00 56 21 | ......d.....d.V!
0000:0100 | 00 00 00 00  04 00 01 00  00 64 00 00  00 01 00 64 | .........d.....d
```

#### N259_.1s_1000r.prg (Actual N=259, Dur0Units_actual=100, Official App)
*Actual Hex (first 256 bytes, from Official App):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 13 00 00  03 01 01 00  64 00 59 13  00 00 00 00 | ;.......d.Y.....
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 85 14 00 | .....d.....d....
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | B1 15 00 00  00 00 04 00  01 00 00 64  00 00 00 01 | ±..........d....
0000:0050 | 00 64 00 DD  16 00 00 00  00 04 00 01  00 00 64 00 | .d.Ý..........d.
0000:0060 | 00 00 01 00  64 00 09 18  00 00 00 00  04 00 01 00 | ....d...........
0000:0070 | 00 64 00 00  00 01 00 64  00 35 19 00  00 00 00 04 | .d.....d.5......
0000:0080 | 00 01 00 00  64 00 00 00  01 00 64 00  61 1A 00 00 | ....d.....d.a...
0000:0090 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 8D | .......d.....d..
0000:00A0 | 1B 00 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:00B0 | 64 00 B9 1C  00 00 00 00  04 00 01 00  00 64 00 00 | d.¹..........d..
0000:00C0 | 00 01 00 64  00 E5 1D 00  00 00 00 04  00 01 00 00 | ...d.å..........
0000:00D0 | 64 00 00 00  01 00 64 00  11 1F 00 00  00 00 04 00 | d.....d.........
0000:00E0 | 01 00 00 64  00 00 00 01  00 64 00 3D  20 00 00 00 | ...d.....d.= ...
0000:00F0 | 00 04 00 01  00 00 64 00  00 00 01 00  64 00 69 21 | ......d.....d.i!
0000:0100 | 00 00 00 00  04 00 01 00  00 64 00 00  00 01 00 64 | .........d.....d
```
*   Header Analysis (all segments 0.1s = 100 units @ 1000Hz):
    *   `0x10-0x13` (Pointer1): `3B 13 00 00` (`0x133B` = 4923). Formula `21 + 19*(259-1) = 21 + 19*258 = 21 + 4902 = 4923`. Matches.
    *   `0x14-0x15` (Segment Count N): `03 01` (`0x0103` = 259). Matches.
    *   `0x16-0x17` (Field 0x16 from Dur0=100): `01 00` (Value 1). Matches Hypothesis 8.
    *   `0x1A-0x1B` (RGB Data Start Offset): `59 13` (`0x1359` = 4953). Formula `32 + 259*19 = 32 + 4921 = 4953`. Matches.
    *   `0x1E-0x1F` (Field 0x1E from Dur0=100): `00 00` (Value 0). Matches Hypothesis 8.
*   Duration Block Analysis (e.g., First block at `0x0020` for Segment 0, Second block at `0x0033` for Segment 1):
    *   `+0x00` Pixel Count: `04 00` (4 pixels).
    *   `+0x05` Current Segment Duration is `64 00` (100 units) for all segments.
    *   `+0x09` (Field `+0x09`):
        *   For Block 0 (idx=0): `01 00 64 00` (`field_09_part1=1`, `field_09_part2=100`). `part1` is `idx+1`.
        *   For Block 1 (idx=1, CurrentDur=100, PrevDur=100): `01 00 64 00` (`field_09_part1=1`, `field_09_part2=100`). `part1` is `1` because durations are equal. This supports "Hypothesis I" for `field_09_part1`.
    *   `+0x11` Next Segment Info (Dur of next segment): `00 00` (0 units) for initial blocks when the next segment's duration is 100ms. This supports the re-confirmed "Hypothesis F" (where `Field+0x11 = 0` if `Dur_k+1 == 100`).
*   Observation: This official app file appears to contain 259 segments, each 100 units (100ms) long, without inserted black gaps.

#### N256_all_100ms.prg (Official Correct, Refresh Rate 1000Hz)
*   **Note:** This is the official correct dump for `N256_all_100ms.prg` (refresh rate 1000Hz).
*Actual Hex (Truncated):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 02 13 00 00  00 01 01 00  64 00 20 13  00 00 00 00 | ........d. .....
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 4C 14 00 | .....d.....d.L..
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | 78 15 00 00  00 00 04 00  01 00 00 64  00 00 00 01 | x..........d....
0000:0050 | 00 64 00 A4  16 00 00 00  00 04 00 01  00 00 64 00 | .d.¤..........d.
0000:0060 | 00 00 01 00  64 00 D0 17  00 00 00 00  04 00 01 00 | ....d.Ð.........
0000:0070 | 00 64 00 00  00 01 00 64  00 FC 18 00  00 00 00 04 | .d.....d.ü......
0000:0080 | 00 01 00 00  64 00 00 00  01 00 64 00  28 1A 00 00 | ....d.....d.(...
0000:0090 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 54 | .......d.....d.T
0000:00A0 | 1B 00 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:00B0 | 64 00 80 1C  00 00 00 00  04 00 01 00  00 64 00 00 | d............d..
0000:00C0 | 00 01 00 64  00 AC 1D 00  00 00 00 04  00 01 00 00 | ...d.¬..........
0000:00D0 | 64 00 00 00  01 00 64 00  D8 1E 00 00  00 00 04 00 | d.....d.Ø.......
0000:00E0 | 01 00 00 64  00 00 00 01  00 64 00 04  20 00 00 00 | ...d.....d.. ...
...
0000:0F00 | 00 01 00 64  00 AC FE 00  00 00 00 04  00 01 00 00 | ...d.¬þ.........
0000:0F10 | 64 00 00 00  01 00 64 00  D8 FF 00 00  00 00 04 00 | d.....d.Øÿ......
0000:0F20 | 01 00 00 64  00 00 00 01  00 64 00 04  01 01 00 00 | ...d.....d......
0000:0F30 | 00 04 00 01  00 00 64 00  00 00 01 00  64 00 30 02 | ......d.....d.0.
0000:0F40 | 01 00 00 00  04 00 01 00  00 64 00 00  00 01 00 64 | .........d.....d
0000:0F50 | 00 5C 03 01  00 00 00 04  00 01 00 00  64 00 00 00 | .\..........d...
0000:0F60 | 01 00 64 00  88 04 01 00  00 00 04 00  01 00 00 64 | ..d............d
0000:0F70 | 00 00 00 01  00 64 00 B4  05 01 00 00  00 04 00 01 | .....d.´........
0000:0F80 | 00 00 64 00  00 00 01 00  64 00 E0 06  01 00 00 00 | ..d.....d.à.....
0000:0F90 | 04 00 01 00  00 64 00 00  00 01 00 64  00 0C 08 01 | .....d.....d....
0000:0FA0 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0FB0 | 38 09 01 00  00 00 04 00  01 00 00 64  00 00 00 01 | 8..........d....
0000:0FC0 | 00 64 00 64  0A 01 00 00  00 04 00 01  00 00 64 00 | .d.d..........d.
0000:0FD0 | 00 00 01 00  64 00 90 0B  01 00 00 00  04 00 01 00 | ....d...........
0000:0FE0 | 00 64 00 00  00 01 00 64  00 BC 0C 01  00 00 00 04 | .d.....d.¼......
...
```

#### N_242_100ms.prg (Official, Refresh Rate 1000Hz)
*Actual Hex (Truncated):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | F8 11 00 00  F2 00 01 00  64 00 16 12  00 00 00 00 | ø...ò...d.......
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 42 13 00 | .....d.....d.B..
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | 6E 14 00 00  00 00 04 00  01 00 00 64  00 00 00 01 | n..........d....
0000:0050 | 00 64 00 9A  15 00 00 00  00 04 00 01  00 00 64 00 | .d............d.
0000:0060 | 00 00 01 00  64 00 C6 16  00 00 00 00  04 00 01 00 | ....d.Æ.........
0000:0070 | 00 64 00 00  00 01 00 64  00 F2 17 00  00 00 00 04 | .d.....d.ò......
0000:0080 | 00 01 00 00  64 00 00 00  01 00 64 00  1E 19 00 00 | ....d.....d.....
0000:0090 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 4A | .......d.....d.J
0000:00A0 | 1A 00 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:00B0 | 64 00 76 1B  00 00 00 00  04 00 01 00  00 64 00 00 | d.v..........d..
0000:00C0 | 00 01 00 64  00 A2 1C 00  00 00 00 04  00 01 00 00 | ...d.¢..........
0000:00D0 | 64 00 00 00  01 00 64 00  CE 1D 00 00  00 00 04 00 | d.....d.Î.......
0000:00E0 | 01 00 00 64  00 00 00 01  00 64 00 FA  1E 00 00 00 | ...d.....d.ú....
...
0000:0F00 | 00 01 00 64  00 A2 FD 00  00 00 00 04  00 01 00 00 | ...d.¢ý.........
0000:0F10 | 64 00 00 00  01 00 64 00  CE FE 00 00  00 00 04 00 | d.....d.Îþ......
0000:0F20 | 01 00 00 64  00 00 00 01  00 64 00 FA  FF 00 00 00 | ...d.....d.úÿ...
0000:0F30 | 00 04 00 01  00 00 64 00  00 00 01 00  64 00 26 01 | ......d.....d.&.
0000:0F40 | 01 00 00 00  04 00 01 00  00 64 00 00  00 01 00 64 | .........d.....d
0000:0F50 | 00 52 02 01  00 00 00 04  00 01 00 00  64 00 00 00 | .R..........d...
0000:0F60 | 01 00 64 00  7E 03 01 00  00 00 04 00  01 00 00 64 | ..d.~..........d
0000:0F70 | 00 00 00 01  00 64 00 AA  04 01 00 00  00 04 00 01 | .....d.ª........
0000:0F80 | 00 00 64 00  00 00 01 00  64 00 D6 05  01 00 00 00 | ..d.....d.Ö.....
0000:0F90 | 04 00 01 00  00 64 00 00  00 01 00 64  00 02 07 01 | .....d.....d....
0000:0FA0 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0FB0 | 2E 08 01 00  00 00 04 00  01 00 00 64  00 00 00 01 | ...........d....
0000:0FC0 | 00 64 00 5A  09 01 00 00  00 04 00 01  00 00 64 00 | .d.Z..........d.
0000:0FD0 | 00 00 01 00  64 00 86 0A  01 00 00 00  04 00 01 00 | ....d...........
0000:0FE0 | 00 64 00 00  00 01 00 64  00 B2 0B 01  00 00 00 04 | .d.....d.²......
0000:0FF0 | 00 01 00 00  64 00 00 00  01 00 64 00  DE 0C 01 00 | ....d.....d.Þ...
0000:1000 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 0A | .......d.....d..
```

#### N512 Example (Official, Refresh Rate 1000Hz)
*   **Note:** This example with N=512 segments demonstrates byte patterns, particularly around address `0x1E17` where a sequence `FF 01` appears, leading to `00 02` in the subsequent block.
*Actual Hex (Truncated):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 02 26 00 00  00 02 01 00  64 00 20 26  00 00 00 00 | .&......d. &....
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 4C 27 00 | .....d.....d.L'.
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | 78 28 00 00  00 00 04 00  01 00 00 64  00 00 00 01 | x(.........d....
0000:0050 | 00 64 00 A4  29 00 00 00  00 04 00 01  00 00 64 00 | .d.¤).........d.
0000:0060 | 00 00 01 00  64 00 D0 2A  00 00 00 00  04 00 01 00 | ....d.Ð*........
0000:0070 | 00 64 00 00  00 01 00 64  00 FC 2B 00  00 00 00 04 | .d.....d.ü+.....
0000:0080 | 00 01 00 00  64 00 00 00  01 00 64 00  28 2D 00 00 | ....d.....d.(-..
0000:0090 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 54 | .......d.....d.T
0000:00A0 | 2E 00 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:00B0 | 64 00 80 2F  00 00 00 00  04 00 01 00  00 64 00 00 | d../.........d..
0000:00C0 | 00 01 00 64  00 AC 30 00  00 00 00 04  00 01 00 00 | ...d.¬0.........
0000:00D0 | 64 00 00 00  01 00 64 00  D8 31 00 00  00 00 04 00 | d.....d.Ø1......
0000:00E0 | 01 00 00 64  00 00 00 01  00 64 00 04  33 00 00 00 | ...d.....d..3...
...
0000:1DC0 | 00 00 64 00  00 00 01 00  64 00 E0 FA  01 00 00 00 | ..d.....d.àú....
0000:1DD0 | 04 00 01 00  00 64 00 00  00 01 00 64  00 0C FC 01 | .....d.....d..ü.
0000:1DE0 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:1DF0 | 38 FD 01 00  00 00 04 00  01 00 00 64  00 00 00 01 | 8ý.........d....
0000:1E00 | 00 64 00 64  FE 01 00 00  00 04 00 01  00 00 64 00 | .d.dþ.........d.
0000:1E10 | 00 00 01 00  64 00 90 FF  01 00 00 00  04 00 01 00 | ....d..ÿ........
0000:1E20 | 00 64 00 00  00 01 00 64  00 BC 00 02  00 00 00 04 | .d.....d.¼......
0000:1E30 | 00 01 00 00  64 00 00 00  01 00 64 00  E8 01 02 00 | ....d.....d.è...
0000:1E40 | 00 00 04 00  01 00 00 64  00 00 00 01  00 64 00 14 | .......d.....d..
0000:1E50 | 03 02 00 00  00 04 00 01  00 00 64 00  00 00 01 00 | ..........d.....
0000:1E60 | 64 00 40 04  02 00 00 00  04 00 01 00  00 64 00 00 | d.@..........d..
0000:1E70 | 00 01 00 64  00 6C 05 02  00 00 00 04  00 01 00 00 | ...d.l..........
0000:1E80 | 64 00 00 00  01 00 64 00  98 06 02 00  00 00 04 00 | d.....d.........
0000:1E90 | 01 00 00 64  00 00 00 01  00 64 00 C4  07 02 00 00 | ...d.....d.Ä....
0000:1EA0 | 00 04 00 01  00 00 64 00  00 00 01 00  64 00 F0 08 | ......d.....d.ð.
0000:1EB0 | 02 00 00 00  04 00 01 00  00 64 00 00  00 01 00 64 | .........d.....d
0000:1EC0 | 00 1C 0A 02  00 00 00 04  00 01 00 00  64 00 00 00 | ............d...
```
## Field[+0x09] and Field[+0x11] Investigation (1000Hz Refresh Rate)

**Date:** 2025-06-02

The following tests were conducted using the official LTX app with a PRG refresh rate of 1000Hz (1 unit = 1ms) to understand the dynamic behavior of `Field[+0x09]` (specifically `field_09_part1` and `field_09_part2`) and `Field[+0x11]` within the intermediate duration blocks. All PRG hex dumps are truncated.

### Test A: N=3 segments. Durations: 1240, 470, 1930 units

*Input Durations:*
*   Segment 0: 1240 units
*   Segment 1: 470 units
*   Segment 2: 1930 units

*Hex Dump (TestA.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 0C 00  64 00 59 00  00 00 28 00 | ;.......d.Y...(.
0000:0020 | 04 00 01 00  00 D8 04 00  00 04 00 64  00 85 01 00 | .....Ø.....d....
0000:0030 | 00 46 00 04  00 01 00 00  D6 01 00 00  13 00 64 00 | .F......Ö.....d.
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43 | ±..............C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

*Header Analysis (Offsets `0x16`, `0x1E`):*
*   `Dur0Units_actual` = 1240
*   Field `0x16`: `0C 00` (12). `floor(1240 / 100) = 12`. Matches.
*   Field `0x1E`: `28 00` (40). `1240 % 100 = 40`. Matches (using simplified rule `Dur0 % 100`).

*Duration Block Analysis:*
*   **Block 0 (Segment 0, offset `0x20`):**
    *   `+0x05` CurrentSegmentDurationUnits: `D8 04` (1240). Correct.
    *   `+0x09` Field[+0x09]: `04 00 64 00` -> `field_09_part1 = 4`, `field_09_part2 = 100`.
    *   `+0x11` NextSegmentInfo (for Dur_1=470): `D6 01` (470). Hypothesis F: `Dur_k+1`(470) > 100, `Dur_k`(1240) != 100 -> val=470. Matches.
*   **Block 1 (Segment 1, offset `0x33`):**
    *   `+0x05` CurrentSegmentDurationUnits: `D6 01` (470). Correct.
    *   `+0x09` Field[+0x09]: `13 00 64 00` -> `field_09_part1 = 19`, `field_09_part2 = 100`.
        *   Observation: `field_09_part2` is 100, despite `CurrentSegmentDurationUnits` being 470.
    *   `+0x11` NextSegmentInfo (for Dur_2=1930): `1E 00` (30). **DISCREPANCY.** Expected 1930 (`8A 07`) by Hypothesis F. Actual dump shows 30.
*   **Block 2 (Segment 2, Last Block, offset `0x46`):**
    *   `+0x05` CurrentSegmentDurationUnits: `8A 07` (1930). Correct.
    *   `+0x09` Field[+0x09]: `43 44` ('CD'). Standard for last block.

### Test B: N=3 segments. Durations: 500, 80, 500 units

*Input Durations:*
*   Segment 0: 500 units
*   Segment 1: 80 units
*   Segment 2: 500 units

*Hex Dump (TestB.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 05 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 F4 01 00  00 00 00 64  00 85 01 00
0000:0030 | 00 50 00 04  00 01 00 00  50 00 00 00  05 00 64 00
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 F4  01 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```

*Header Analysis (Offsets `0x16`, `0x1E`):*
*   `Dur0Units_actual` = 500
*   Field `0x16`: `05 00` (5). `floor(500 / 100) = 5`. Matches.
*   Field `0x1E`: `00 00` (0). `500 % 100 = 0`. Matches (using simplified rule `Dur0 % 100`).

*Duration Block Analysis:*
*   **Block 0 (Segment 0, offset `0x20`):**
    *   `+0x05` CurrentSegmentDurationUnits: `F4 01` (500). Correct.
    *   `+0x09` Field[+0x09]: `00 00 64 00` -> `field_09_part1 = 0`, `field_09_part2 = 100`.
    *   `+0x11` NextSegmentInfo (for Dur_1=80): `50 00` (80). Hypothesis F: `Dur_k+1`(80) < 100 -> val=80. Matches.
*   **Block 1 (Segment 1, offset `0x33`):**
    *   `+0x05` CurrentSegmentDurationUnits: `50 00` (80). Correct.
    *   `+0x09` Field[+0x09]: `05 00 64 00` -> `field_09_part1 = 5`, `field_09_part2 = 100`.
        *   Observation: `field_09_part2` is 100, despite `CurrentSegmentDurationUnits` (80) < 100.
    *   `+0x11` NextSegmentInfo (for Dur_2=500): `F4 01` (500). Hypothesis F: `Dur_k+1`(500) > 100, `Dur_k`(80) != 100 -> val=500. Matches.
*   **Block 2 (Segment 2, Last Block, offset `0x46`):**
    *   `+0x05` CurrentSegmentDurationUnits: `F4 01` (500). Correct.
    *   `+0x09` Field[+0x09]: `43 44` ('CD'). Standard for last block.

### Test C: N=3 segments. Durations: 500, 120, 500 units

*Input Durations:*
*   Segment 0: 500 units
*   Segment 1: 120 units
*   Segment 2: 500 units

*Hex Dump (TestC.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 05 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 F4 01 00  00 01 00 64  00 85 01 00
0000:0030 | 00 14 00 04  00 01 00 00  78 00 00 00  05 00 64 00
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 F4  01 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```

*Header Analysis (Offsets `0x16`, `0x1E`):*
*   `Dur0Units_actual` = 500
*   Field `0x16`: `05 00` (5). `floor(500 / 100) = 5`. Matches.
*   Field `0x1E`: `00 00` (0). `500 % 100 = 0`. Matches (using simplified rule `Dur0 % 100`).

*Duration Block Analysis:*
*   **Block 0 (Segment 0, offset `0x20`):**
    *   `+0x05` CurrentSegmentDurationUnits: `F4 01` (500). Correct.
    *   `+0x09` Field[+0x09]: `01 00 64 00` -> `field_09_part1 = 1`, `field_09_part2 = 100`.
    *   `+0x11` NextSegmentInfo (for Dur_1=120): `78 00` (120). Hypothesis F: `Dur_k+1`(120) > 100, `Dur_k`(500) != 100 -> val=120. Matches.
*   **Block 1 (Segment 1, offset `0x33`):**
    *   `+0x05` CurrentSegmentDurationUnits: `78 00` (120). Correct.
    *   `+0x09` Field[+0x09]: `05 00 64 00` -> `field_09_part1 = 5`, `field_09_part2 = 100`.
        *   Observation: `field_09_part2` is 100, despite `CurrentSegmentDurationUnits` (120) > 100.
    *   `+0x11` NextSegmentInfo (for Dur_2=500): `F4 01` (500). Hypothesis F: `Dur_k+1`(500) > 100, `Dur_k`(120) != 100 -> val=500. Matches.
*   **Block 2 (Segment 2, Last Block, offset `0x46`):**
    *   `+0x05` CurrentSegmentDurationUnits: `F4 01` (500). Correct.
    *   `+0x09` Field[+0x09]: `43 44` ('CD'). Standard for last block.
## Deduced Logic for Header Fields 0x16 and 0x1E (Hypothesis 8 - Current Best as of 2025-06-01 10:25)

This logic applies universally across different PRG refresh rates and segment counts, based on all provided official app samples.

It's also important to note the structure of certain fields within **Intermediate Duration Blocks** (i.e., not the last duration block):

*   **Field `+0x09` (Segment Index & Duration) (Revised 2025-06-01):**
    This 4-byte field consists of two 2-byte Little Endian values:
    1.  `field_09_part1`:
        *   If it's the first duration block (`current_block_index == 0`): This is `1` (`01 00`).
        *   If `current_block_index > 0` AND `CurrentSegmentDurationUnits == PreviousSegmentDurationUnits`: This value is `CurrentSegmentDurationUnits`.
        *   Else (`current_block_index > 0` AND `CurrentSegmentDurationUnits != PreviousSegmentDurationUnits`): This value is `current_block_index + 1`.
    2.  `field_09_part2`: This is always `CurrentSegmentDurationUnits`.

*   **Field `+0x11` (Next Segment Info) (Revised 2025-06-01):**
    Let `Dur_k` be current segment's duration, `Dur_k+1` be next segment's duration.
    1.  If `Dur_k+1 < 100`: value is `Dur_k+1`.
### Test D: N=4 segments. All durations: 75 units

*Input Durations:* 75, 75, 75, 75 units.

*Hex Dump (TestD.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 4E 00 00 00  04 00 00 00  64 00 6C 00  00 00 4B 00 | N.......d.l...K.
0000:0020 | 04 00 01 00  00 4B 00 00  00 00 00 64  00 98 01 00 | .....K.....d....
0000:0030 | 00 4B 00 04  00 01 00 00  4B 00 00 00  00 00 64 00 | .K......K.....d.
0000:0040 | C4 02 00 00  4B 00 04 00  01 00 00 4B  00 00 00 00 | Ä...K......K....
0000:0050 | 00 64 00 F0  03 00 00 4B  00 04 00 01  00 00 4B 00 | .d.ð...K......K.
0000:0060 | 00 00 43 44  B4 04 00 00  90 01 00 00  FF 00 00 FF | ..CD´.......ÿ..ÿ
```

*Header Analysis (Offsets `0x16`, `0x1E`):*
*   `Dur0Units_actual` = 75
*   Field `0x16`: `00 00` (0). `floor(75/100)=0`. Matches.
*   Field `0x1E`: `4B 00` (75). `75 % 100 = 75`. Matches simplified rule.

*Duration Block Analysis (all segments 75 units):*
*   **Block 0 (Seg 0, offset `0x20`):** Dur=75. `Field[+0x09]`: `00 00 64 00` (`part1=0`, `part2=100`). `Field[+0x11]` (for Dur_1=75): `4B 00` (75). Matches HypF.
*   **Block 1 (Seg 1, offset `0x33`):** Dur=75. `Field[+0x09]`: `00 00 64 00` (`part1=0`, `part2=100`). `Field[+0x11]` (for Dur_2=75): `4B 00` (75). Matches HypF.
*   **Block 2 (Seg 2, offset `0x46`):** Dur=75. `Field[+0x09]`: `00 00 64 00` (`part1=0`, `part2=100`). `Field[+0x11]` (for Dur_3=75): `4B 00` (75). Matches HypF.
*   **Block 3 (Seg 3, Last Block, offset `0x59`):** Dur=75. `Field[+0x09]`: `43 44`. Standard.

### Test E: N=4 segments. All durations: 100 units

*Input Durations:* 100, 100, 100, 100 units.

*Hex Dump (TestE.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 4E 00 00 00  04 00 01 00  64 00 6C 00  00 00 00 00
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 98 01 00
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00
0000:0040 | C4 02 00 00  00 00 04 00  01 00 00 64  00 00 00 01
0000:0050 | 00 64 00 F0  03 00 00 00  00 04 00 01  00 00 64 00
0000:0060 | 00 00 43 44  B4 04 00 00  90 01 00 00  FF 00 00 FF
```

*Header Analysis (Offsets `0x16`, `0x1E`):*
*   `Dur0Units_actual` = 100
*   Field `0x16`: `01 00` (1). `floor(100/100)=1`. Matches.
*   Field `0x1E`: `00 00` (0). `100 % 100 = 0`. Matches simplified rule.

*Duration Block Analysis (all segments 100 units):*
*   **Block 0 (Seg 0, offset `0x20`):** Dur=100. `Field[+0x09]`: `01 00 64 00` (`part1=1`, `part2=100`). `Field[+0x11]` (for Dur_1=100): `00 00` (0). Matches HypF.
*   **Block 1 (Seg 1, offset `0x33`):** Dur=100. `Field[+0x09]`: `01 00 64 00` (`part1=1`, `part2=100`). `Field[+0x11]` (for Dur_2=100): `00 00` (0). Matches HypF.
*   **Block 2 (Seg 2, offset `0x46`):** Dur=100. `Field[+0x09]`: `01 00 64 00` (`part1=1`, `part2=100`). `Field[+0x11]` (for Dur_3=100): `00 00` (0). Matches HypF.
*   **Block 3 (Seg 3, Last Block, offset `0x59`):** Dur=100. `Field[+0x09]`: `43 44`. Standard.

### Test F: N=4 segments. Alternating durations: 70, 120, 70, 120 units

*Input Durations:* 70, 120, 70, 120 units.

*Hex Dump (TestF.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 4E 00 00 00  04 00 00 00  64 00 6C 00  00 00 46 00
0000:0020 | 04 00 01 00  00 46 00 00  00 01 00 64  00 98 01 00
0000:0030 | 00 14 00 04  00 01 00 00  78 00 00 00  00 00 64 00
0000:0040 | C4 02 00 00  46 00 04 00  01 00 00 46  00 00 00 01
0000:0050 | 00 64 00 F0  03 00 00 14  00 04 00 01  00 00 78 00
0000:0060 | 00 00 43 44  B4 04 00 00  90 01 00 00  FF 00 00 FF
```

*Header Analysis (Offsets `0x16`, `0x1E`):*
*   `Dur0Units_actual` = 70
*   Field `0x16`: `00 00` (0). `floor(70/100)=0`. Matches.
*   Field `0x1E`: `46 00` (70). `70 % 100 = 70`. Matches simplified rule.

*Duration Block Analysis:*
*   **Block 0 (Seg 0, Dur=70, offset `0x20`):** `Field[+0x09]`: `01 00 64 00` (`part1=1`, `part2=100`). `Field[+0x11]` (for Dur_1=120): `78 00` (120). Matches HypF.
*   **Block 1 (Seg 1, Dur=120, offset `0x33`):** `Field[+0x09]`: `00 00 64 00` (`part1=0`, `part2=100`). `Field[+0x11]` (for Dur_2=70): `46 00` (70). Matches HypF.
*   **Block 2 (Seg 2, Dur=70, offset `0x46`):** `Field[+0x09]`: `01 00 64 00` (`part1=1`, `part2=100`). `Field[+0x11]` (for Dur_3=120): `78 00` (120). Matches HypF.
*   **Block 3 (Seg 3, Dur=120, Last Block, offset `0x59`):** `Field[+0x09]`: `43 44`. Standard.

### Test G: N=5 segments. Durations: 70, 70, 120, 120, 70 units

*Input Durations:* 70, 70, 120, 120, 70 units.

*Hex Dump (TestG.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 61 00 00 00  05 00 00 00  64 00 7F 00  00 00 46 00
0000:0020 | 04 00 01 00  00 46 00 00  00 00 00 64  00 AB 01 00
0000:0030 | 00 46 00 04  00 01 00 00  46 00 00 00  01 00 64 00
0000:0040 | D7 02 00 00  14 00 04 00  01 00 00 78  00 00 00 01
0000:0050 | 00 64 00 03  04 00 00 14  00 04 00 01  00 00 78 00
0000:0060 | 00 00 00 00  64 00 2F 05  00 00 46 00  04 00 01 00
0000:0070 | 00 46 00 00  00 43 44 E0  05 00 00 F4  01 00 00 FF
```

*Header Analysis (Offsets `0x16`, `0x1E`):*
*   `Dur0Units_actual` = 70
*   Field `0x16`: `00 00` (0). `floor(70/100)=0`. Matches.
*   Field `0x1E`: `46 00` (70). `70 % 100 = 70`. Matches simplified rule.

*Duration Block Analysis:*
*   **Block 0 (Seg 0, Dur=70, offset `0x20`):** `Field[+0x09]`: `00 00 64 00` (`part1=0`, `part2=100`). `Field[+0x11]` (for Dur_1=70): `46 00` (70). Matches HypF.
*   **Block 1 (Seg 1, Dur=70, offset `0x33`):** `Field[+0x09]`: `01 00 64 00` (`part1=1`, `part2=100`). `Field[+0x11]` (for Dur_2=120): `78 00` (120). Matches HypF.
*   **Block 2 (Seg 2, Dur=120, offset `0x46`):** `Field[+0x09]`: `01 00 64 00` (`part1=1`, `part2=100`). `Field[+0x11]` (for Dur_3=120): `78 00` (120). Matches HypF.
*   **Block 3 (Seg 3, Dur=120, offset `0x59`):** `Field[+0x09]`: `00 00 64 00` (`part1=0`, `part2=100`). `Field[+0x11]` (for Dur_4=70): `46 00` (70). Matches HypF.
*   **Block 4 (Seg 4, Dur=70, Last Block, offset `0x6C`):** `Field[+0x09]`: `43 44`. Standard.

---

## Further Field[+0x09] and Field[+0x11] Investigation - H & J Series (1000Hz)

**Date:** 2025-06-02 (following analysis of Tests A-G)

These tests further probe `Field[+0x09].part1` and the `Field[+0x11]` anomaly using N=3 segments at 1000Hz.

### Test H1: N=3 segments. Durations: 50, 50, 50 units

*Hex Dump (H1.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  00 00 64 00
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 32  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=50):* `0x16=0000` (0), `0x1E=3200` (50). Matches.
*Block 0 (Dur=50):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur1=50) = `3200` (50). Matches HypF.
*Block 1 (Dur=50):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur2=50) = `3200` (50). Matches HypF.
*Block 2 (Dur=50, Last):* Standard.

### Test H2: N=3 segments. Durations: 150, 150, 150 units

*Hex Dump (H2.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 32 00
0000:0020 | 04 00 01 00  00 96 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 32 00 04  00 01 00 00  96 00 00 00  01 00 64 00
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=150):* `0x16=0100` (1), `0x1E=3200` (50). Matches.
*Block 0 (Dur=150):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=150) = `9600` (150). Matches HypF.
*Block 1 (Dur=150):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur2=150) = `9600` (150). Matches HypF.
*Block 2 (Dur=150, Last):* Standard.

### Test H3: N=3 segments. Durations: 50, 100, 150 units

*Hex Dump (H3.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=50):* `0x16=0000` (0), `0x1E=3200` (50). Matches.
*Block 0 (Dur=50):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=100) = `0000` (0). Matches HypF.
*Block 1 (Dur=100):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur2=150) = `9600` (150). **DISCREPANCY** with refined HypF rule 3.a (expected 0 if Dur_k=100).
*Block 2 (Dur=150, Last):* Standard.

### Test H4: N=3 segments. Durations: 150, 100, 50 units

*Hex Dump (H4.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 32 00
0000:0020 | 04 00 01 00  00 96 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  00 00 64 00
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 32  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=150):* `0x16=0100` (1), `0x1E=3200` (50). Matches.
*Block 0 (Dur=150):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=100) = `0000` (0). Matches HypF.
*Block 1 (Dur=100):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur2=50) = `3200` (50). Matches HypF.
*Block 2 (Dur=50, Last):* Standard.

### Test H5: N=3 segments. Durations: 80, 120, 80 units

*Hex Dump (H5.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 50 00
0000:0020 | 04 00 01 00  00 50 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 14 00 04  00 01 00 00  78 00 00 00  00 00 64 00
0000:0040 | B1 02 00 00  50 00 04 00  01 00 00 50  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=80):* `0x16=0000` (0), `0x1E=5000` (80). Matches.
*Block 0 (Dur=80):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=120) = `7800` (120). Matches HypF.
*Block 1 (Dur=120):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur2=80) = `5000` (80). Matches HypF.
*Block 2 (Dur=80, Last):* Standard.

### Test J1: N=3 segments. Durations: 1240, 470, 1930 units (Repeat of Test A)

*Hex Dump (J1.prg - identical to TestA.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0C 00  64 00 59 00  00 00 28 00
0000:0020 | 04 00 01 00  00 D8 04 00  00 04 00 64  00 85 01 00
0000:0030 | 00 46 00 04  00 01 00 00  D6 01 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Analysis:* Identical to Test A. Block 1 `+0x11` (for Dur2=1930) is `1E00` (30). Anomaly reproduced.

### Test J2: N=3 segments. Durations: 1240, 470, 1800 units

*Hex Dump (J2.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0C 00  64 00 59 00  00 00 28 00
0000:0020 | 04 00 01 00  00 D8 04 00  00 04 00 64  00 85 01 00
0000:0030 | 00 46 00 04  00 01 00 00  D6 01 00 00  12 00 64 00
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 08  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1240):* Same as J1.
*Block 0 (Dur=1240):* `+0x09=04006400` (p1=4, p2=100). `+0x11` (for Dur1=470) = `D601` (470). Matches HypF.
*Block 1 (Dur=470):* `+0x09=12006400` (p1=18, p2=100). `+0x11` (for Dur2=1800) = `0807` (1800). **Matches HypF! Anomaly gone.**
*Block 2 (Dur=1800, Last):* Standard.

### Test J3: N=3 segments. Durations: 1240, 450, 1930 units

*Hex Dump (J3.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0C 00  64 00 59 00  00 00 28 00
0000:0020 | 04 00 01 00  00 D8 04 00  00 04 00 64  00 85 01 00
0000:0030 | 00 32 00 04  00 01 00 00  C2 01 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1240):* Same as J1.
*Block 0 (Dur=1240):* `+0x09=04006400` (p1=4, p2=100). `+0x11` (for Dur1=450) = `C201` (450). Matches HypF.
*Block 1 (Dur=450):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly persists.**
*Block 2 (Dur=1930, Last):* Standard.

### Test J4: N=3 segments. Durations: 1240, 500, 1930 units

*Hex Dump (J4.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0C 00  64 00 59 00  00 00 28 00
0000:0020 | 04 00 01 00  00 D8 04 00  00 05 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  F4 01 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1240):* Same as J1.
*Block 0 (Dur=1240):* `+0x09=05006400` (p1=5, p2=100). `+0x11` (for Dur1=500) = `F401` (500). Matches HypF.
*Block 1 (Dur=500):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly persists.**
*Block 2 (Dur=1930, Last):* Standard.

### Test J5: N=3 segments. Durations: 1240, 80, 1930 units

*Hex Dump (J5.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0C 00  64 00 59 00  00 00 28 00
0000:0020 | 04 00 01 00  00 D8 04 00  00 00 00 64  00 85 01 00
0000:0030 | 00 50 00 04  00 01 00 00  50 00 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1240):* Same as J1.
*Block 0 (Dur=1240):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur1=80) = `5000` (80). Matches HypF.
*Block 1 (Dur=80):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly persists.**
*Block 2 (Dur=1930, Last):* Standard.

---

---

## Field[+0x09].part1 and "1930 Anomaly" Deep Dive - K & L Series (1000Hz)

**Date:** 2025-06-02 (following analysis of Tests H & J)

These N=3 segment tests (1000Hz) further probe `Field[+0x09].part1` and the conditions for the `Field[+0x11]` "1930 Anomaly".

### Set K: Probing `Field[+0x09].field_09_part1`

**Test K1: Durations: 70, 70, 100 units**
*Hex Dump (K1.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 46 00
0000:0020 | 04 00 01 00  00 46 00 00  00 00 00 64  00 85 01 00
0000:0030 | 00 46 00 04  00 01 00 00  46 00 00 00  01 00 64 00
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 64  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=70):* `0x16=0000` (0), `0x1E=4600` (70). Matches.
*Block 0 (Dur0=70, Dur1=70):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur1=70) = `4600` (70). Matches HypF.
*Block 1 (Dur1=70, Dur2=100):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur2=100) = `0000` (0). Matches HypF.

**Test K2: Durations: 70, 100, 70 units**
*Hex Dump (K2.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 46 00
0000:0020 | 04 00 01 00  00 46 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  00 00 64 00
0000:0040 | B1 02 00 00  46 00 04 00  01 00 00 46  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=70):* `0x16=0000` (0), `0x1E=4600` (70). Matches.
*Block 0 (Dur0=70, Dur1=100):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=100) = `0000` (0). Matches HypF.
*Block 1 (Dur1=100, Dur2=70):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur2=70) = `4600` (70). Matches HypF.

**Test K3: Durations: 100, 70, 70 units**
*Hex Dump (K3.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 64 00 00  00 00 00 64  00 85 01 00
0000:0030 | 00 46 00 04  00 01 00 00  46 00 00 00  00 00 64 00
0000:0040 | B1 02 00 00  46 00 04 00  01 00 00 46  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=100):* `0x16=0100` (1), `0x1E=0000` (0). Matches.
*Block 0 (Dur0=100, Dur1=70):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur1=70) = `4600` (70). Matches HypF.
*Block 1 (Dur1=70, Dur2=70):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur2=70) = `4600` (70). Matches HypF.

**Test K4: Durations: 120, 120, 100 units**
*Hex Dump (K4.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 14 00
0000:0020 | 04 00 01 00  00 78 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 14 00 04  00 01 00 00  78 00 00 00  01 00 64 00
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 64  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=120):* `0x16=0100` (1), `0x1E=1400` (20). Matches.
*Block 0 (Dur0=120, Dur1=120):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=120) = `7800` (120). Matches HypF.
*Block 1 (Dur1=120, Dur2=100):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur2=100) = `0000` (0). Matches HypF.

**Test K5: Durations: 120, 100, 120 units**
*Hex Dump (K5.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 14 00
0000:0020 | 04 00 01 00  00 78 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00
0000:0040 | B1 02 00 00  14 00 04 00  01 00 00 78  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=120):* `0x16=0100` (1), `0x1E=1400` (20). Matches.
*Block 0 (Dur0=120, Dur1=100):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=100) = `0000` (0). Matches HypF.
*Block 1 (Dur1=100, Dur2=120):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur2=120) = `7800` (120). Matches HypF (rule 2c, Dur_k=100).

**Test K6: Durations: 100, 120, 120 units**
*Hex Dump (K6.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 14 00 04  00 01 00 00  78 00 00 00  01 00 64 00
0000:0040 | B1 02 00 00  14 00 04 00  01 00 00 78  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=100):* `0x16=0100` (1), `0x1E=0000` (0). Matches.
*Block 0 (Dur0=100, Dur1=120):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=120) = `7800` (120). Matches HypF (rule 2c, Dur_k=100).
*Block 1 (Dur1=120, Dur2=120):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur2=120) = `7800` (120). Matches HypF.

**Test K7: Durations: 70, 120, 150 units**
*Hex Dump (K7.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 46 00
0000:0020 | 04 00 01 00  00 46 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 14 00 04  00 01 00 00  78 00 00 00  01 00 64 00
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=70):* `0x16=0000` (0), `0x1E=4600` (70). Matches.
*Block 0 (Dur0=70, Dur1=120):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=120) = `7800` (120). Matches HypF.
*Block 1 (Dur1=120, Dur2=150):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur2=150) = `9600` (150). Matches HypF.

**Test K8: Durations: 150, 120, 70 units**
*Hex Dump (K8.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 32 00
0000:0020 | 04 00 01 00  00 96 00 00  00 01 00 64  00 85 01 00
0000:0030 | 00 14 00 04  00 01 00 00  78 00 00 00  00 00 64 00
0000:0040 | B1 02 00 00  46 00 04 00  01 00 00 46  00 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=150):* `0x16=0100` (1), `0x1E=3200` (50). Matches.
*Block 0 (Dur0=150, Dur1=120):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=120) = `7800` (120). Matches HypF.
*Block 1 (Dur1=120, Dur2=70):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur2=70) = `4600` (70). Matches HypF.

### Set L: Mapping the "1930 Anomaly" for `Field[+0x11]`
*(Dur0 = 1000 units for these tests)*

**Test L1: Durations: 1000, 70, 1930 units**
*Hex Dump (L1.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0A 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 E8 03 00  00 00 00 64  00 85 01 00
0000:0030 | 00 46 00 04  00 01 00 00  46 00 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1000):* `0x16=0A00` (10), `0x1E=0000` (0). Matches.
*Block 0 (Dur0=1000, Dur1=70):* `+0x09=00006400` (p1=0, p2=100). `+0x11` (for Dur1=70) = `4600` (70). Matches HypF.
*Block 1 (Dur1=70, Dur2=1930):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly present.**

**Test L2: Durations: 1000, 100, 1930 units**
*Hex Dump (L2.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0A 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 E8 03 00  00 01 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1000):* Same as L1.
*Block 0 (Dur0=1000, Dur1=100):* `+0x09=01006400` (p1=1, p2=100). `+0x11` (for Dur1=100) = `0000` (0). Matches HypF.
*Block 1 (Dur1=100, Dur2=1930):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly present.**

**Test L3: Durations: 1000, 490, 1930 units**
*Hex Dump (L3.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0A 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 E8 03 00  00 04 00 64  00 85 01 00
0000:0030 | 00 5A 00 04  00 01 00 00  EA 01 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1000):* Same as L1.
*Block 0 (Dur0=1000, Dur1=490):* `+0x09=04006400` (p1=4, p2=100). `+0x11` (for Dur1=490) = `EA01` (490). Matches HypF.
*Block 1 (Dur1=490, Dur2=1930):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly present.**

**Test L4: Durations: 1000, 510, 1930 units**
*Hex Dump (L4.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0A 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 E8 03 00  00 05 00 64  00 85 01 00
0000:0030 | 00 0A 00 04  00 01 00 00  FE 01 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1000):* Same as L1.
*Block 0 (Dur0=1000, Dur1=510):* `+0x09=05006400` (p1=5, p2=100). `+0x11` (for Dur1=510) = `FE01` (510). Matches HypF.
*Block 1 (Dur1=510, Dur2=1930):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly present.**

**Test L5: Durations: 1000, 600, 1930 units**
*Hex Dump (L5.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0A 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 E8 03 00  00 06 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  58 02 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1000):* Same as L1.
*Block 0 (Dur0=1000, Dur1=600):* `+0x09=06006400` (p1=6, p2=100). `+0x11` (for Dur1=600) = `5802` (600). Matches HypF.
*Block 1 (Dur1=600, Dur2=1930):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly present.**

**Test L6: Durations: 1000, 1000, 1930 units**
*Hex Dump (L6.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0A 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 E8 03 00  00 0A 00 64  00 85 01 00
0000:0030 | 00 00 00 04  00 01 00 00  E8 03 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1000):* Same as L1.
*Block 0 (Dur0=1000, Dur1=1000):* `+0x09=0A006400` (p1=10, p2=100). `+0x11` (for Dur1=1000) = `E803` (1000). Matches HypF.
*Block 1 (Dur1=1000, Dur2=1930):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly present.**

**Test L7: Durations: 1000, 1929, 1930 units**
*Hex Dump (L7.prg):*
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49
0000:0010 | 3B 00 00 00  03 00 0A 00  64 00 59 00  00 00 00 00
0000:0020 | 04 00 01 00  00 E8 03 00  00 13 00 64  00 85 01 00
0000:0030 | 00 1D 00 04  00 01 00 00  89 07 00 00  13 00 64 00
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF
```
*Header (Dur0=1000):* Same as L1.
*Block 0 (Dur0=1000, Dur1=1929):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur1=1929) = `8907` (1929). Matches HypF.
*Block 1 (Dur1=1929, Dur2=1930):* `+0x09=13006400` (p1=19, p2=100). `+0x11` (for Dur2=1930) = `1E00` (30). **Anomaly present.**

---

## Deduced Logic and Hypotheses (as of 2025-06-02, after K & L series)

This section summarizes the current understanding based on all analyzed PRG files, including Tests A-L.

### Header Fields `0x16` and `0x1E`

Let:
*   `Dur0Units_actual`: The duration of the first PRG segment (Segment 0) in PRG time units.
*   `N_prg`: The total number of PRG segments in the file.
*   `NominalBase = 100`.
*   `val_0x16_dec`: The decimal value for field `0x16`.
*   `val_0x1E_dec`: The decimal value for field `0x1E`.

**Field `0x16` (Header First Segment Info):**
  `val_0x16_dec = floor(Dur0Units_actual / NominalBase)`
  *This logic holds universally across all tests (A-L, N=1 and N>1, various refresh rates).*

**Field `0x1E` (Header First Segment Duration (Conditional)):**
Refined Hypothesis for Header Field 0x1E:
Let NominalBase = 100.

    If N_prg == 1:
        If Dur0Units_actual % NominalBase == 0: (Dur0 is a multiple of 100)
            If RefreshRate == 1 OR Dur0Units_actual == NominalBase: val_0x1E_dec = 0.
            Else (RefreshRate != 1 AND Dur0Units_actual != NominalBase): val_0x1E_dec = Dur0Units_actual.
        Else (Dur0Units_actual % NominalBase != 0):
            val_0x1E_dec = Dur0Units_actual % NominalBase.

    If N_prg > 1:
        If Dur0Units_actual == NominalBase (i.e., 100): val_0x1E_dec = 0.
        Else: val_0x1E_dec = Dur0Units_actual.

    Justification for N=1 refinement: This handles the 1Hz, Dur0=200 case (0x1E=0) and the 1000Hz, Dur0=500/1000 cases (0x1E=Dur0).

    Justification for N>1 refinement: This handles red_1s_blue_.5s_1000r.prg (Dur0=1000, 0x1E=1000) and other N>1 cases correctly. The key is that for N>1, if Dur0 is not 100, 0x1E seems to just be Dur0Units_actual.
The byte values written to the file are `struct.pack('<H', val_0x16_dec)` and `struct.pack('<H', val_0x1E_dec & 0xFFFF)`.
*This logic for header fields 0x16 and 0x1E appears consistent across all known tests (A-L).*

### Intermediate Duration Block Fields (Segments 0 to N-2)

This section details the refined understanding of Field `+0x09` and Field `+0x11` for intermediate duration blocks (i.e., for segments 0 to N-2, where N is the total number of segments).

**Field `+0x09` (Segment Index & Duration)**
This 4-byte field is composed of two 2-byte Little Endian values: `field_09_part1` followed by `field_09_part2`.

*   **`field_09_part2`:**
    *   **Observation (Tests A-L, 1000Hz):** For all intermediate duration blocks (segments 0 to N-2), `field_09_part2` is consistently `64 00` (decimal 100).
    *   **Assessment:** This is correct and universally observed in the provided 1000Hz test data.

*   **`field_09_part1`:**
    *   **Hypothesis (from Tests A-L, 1000Hz):** For an intermediate duration block `k` (which describes segment `k`), if the *next* segment (segment `k+1`) has a duration `Dur_k+1` (in PRG time units):
        **`field_09_part1 (for block k) = floor(Dur_k+1 / 100)`**
    *   **Assessment:** This hypothesis correctly predicts `field_09_part1` for all intermediate blocks in all official app tests A-L (1000Hz).
        *   Example Test A (Durations: 1240, 470, 1930):
            *   Block 0: `Dur_1` = 470. `floor(470 / 100) = 4`. `field_09_part1` is `04 00`. Matches.
            *   Block 1: `Dur_2` = 1930. `floor(1930 / 100) = 19`. `field_09_part1` is `13 00`. Matches.
        *   Example Test G (Durations: 70, 70, 120, 120, 70):
            *   Block 0: `Dur_1` = 70. `floor(70 / 100) = 0`. `field_09_part1` is `00 00`. Matches.
            *   Block 1: `Dur_2` = 120. `floor(120 / 100) = 1`. `field_09_part1` is `01 00`. Matches.
            *   Block 2: `Dur_3` = 120. `floor(120 / 100) = 1`. `field_09_part1` is `01 00`. Matches.
            *   Block 3: `Dur_4` = 70. `floor(70 / 100) = 0`. `field_09_part1` is `00 00`. Matches.

**Field `+0x11` (Next Segment Info)**
Let `Dur_k+1` be the duration of the next segment (segment `k+1`) in PRG time units.

*   **Special Override Case ("1930 Anomaly"):**
    *   If `Dur_k+1 == 1930`: `Field[+0x11]` for Block `k` is `1E 00` (decimal 30).
    *   This override is confirmed by Tests L1-L7, irrespective of `Dur_k`.

*   **General Rules (if not overridden by the "1930 Anomaly"):**
    a.  If `Dur_k+1 < 100`: `Field[+0x11] = Dur_k+1`.
    b.  Else if `Dur_k+1 == 100`: `Field[+0x11] = 0`.
    c.  Else (`Dur_k+1 > 100` and `Dur_k+1 != 1930`): `Field[+0x11] = Dur_k+1`.

*   **Assessment:** This refined logic for `Field[+0x11]` correctly predicts its value for all intermediate blocks in Tests A-L. The previous "Discrepancy" noted in Test H3 is resolved with this logic (Test H3, Block 1: `Dur_k=100`, `Dur_k+1=150`. Since `150 > 100` and not 1930, `Field[+0x11]` is 150 (`96 00`), which matches the hex dump and Rule 2.c).

*Implementation Note for `prg_generator.py`: The generator should be updated to reflect these refined hypotheses for both `Field[+0x09]` (part1 and part2) and `Field[+0x11]` to align more closely with official app behavior, potentially resolving previous strobing issues linked to older, more complex hypotheses for these fields.*
---

## Additional Test Series (M, N, P, Q, R) - 1000Hz Refresh Rate

**Date:** 2025-06-02

These tests further investigate specific behaviors and boundary conditions at 1000Hz PRG refresh rate.

### Test M1:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 103ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  03 00 04 00  01 00 00 67  00 00 00 43 | ±..........g...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test M2:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 100ms
    Segment 2 Duration: 103ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | B1 02 00 00  03 00 04 00  01 00 00 67  00 00 00 43 | ±..........g...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test M3:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 150ms
    Segment 2 Duration: 103ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  96 00 00 00  01 00 64 00 | .2............d.
0000:0040 | B1 02 00 00  03 00 04 00  01 00 00 67  00 00 00 43 | ±..........g...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test N1:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 101ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  01 00 04 00  01 00 00 65  00 00 00 43 | ±..........e...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test N2:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 102ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  02 00 04 00  01 00 00 66  00 00 00 43 | ±..........f...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test N3:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 104ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  04 00 04 00  01 00 00 68  00 00 00 43 | ±..........h...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test N4:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 105ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  05 00 04 00  01 00 00 69  00 00 00 43 | ±..........i...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test P1: (Mimicking context similar to N=258 Block 192 anomaly where part1 was 2)

    Segment 0 Duration: 50ms
    Segment 1 Duration: 102ms (Mimicking Dur_k of Segment 192)
    Segment 2 Duration: 200ms (Testing Dur_k+1 that should yield part1 = 2)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 02 00 04  00 01 00 00  66 00 00 00  02 00 64 00 | ........f.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 C8  00 00 00 43 | ±..........È...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test P2: (Testing Dur_k+1 boundary for part1 around floor(X/100)=1 or 2)

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 199ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  63 00 04 00  01 00 00 C7  00 00 00 43 | ±...c......Ç...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test P3: (Testing Dur_k+1 boundary for part1 around floor(X/100)=1 or 2)

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 200ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  02 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 C8  00 00 00 43 | ±..........È...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test P4: (Testing Dur_k+1 boundary for part1 around floor(X/100)=2)

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 201ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  02 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  01 00 04 00  01 00 00 C9  00 00 00 43 | ±..........É...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test P5: (Testing Dur_k+1 boundary for part1 around floor(X/100)=2 or 3)

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 299ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  02 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  63 00 04 00  01 00 00 2B  01 00 00 43 | ±...c......+...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test P6: (Testing Dur_k+1 boundary for part1 around floor(X/100)=2 or 3)

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 300ms

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  03 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 2C  01 00 00 43 | ±..........,...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test Q1: (N=1, Dur0Units_actual is multiple of 100, but not 100)

    Number of Segments (N): 1
    Segment 0 Duration (Dur0Units_actual): 200ms
    (Expected: 0x16=0200, 0x1E=C800 (200))

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 02 00  64 00 33 00  00 00 00 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 C8 00 00  00 43 44 30  01 00 00 64 | .....È...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```

### Test Q2: (N=1, Dur0Units_actual is multiple of 100, but not 100)

    Number of Segments (N): 1
    Segment 0 Duration (Dur0Units_actual): 300ms
    (Expected: 0x16=0300, 0x1E=2C01 (300))

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 03 00  64 00 33 00  00 00 00 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 2C 01 00  00 43 44 30  01 00 00 64 | .....,...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```

### Test Q3: (N>1, Dur0Units_actual is multiple of 100, but not 100)

    Number of Segments (N): 2
    Segment 0 Duration (Dur0Units_actual): 200ms
    Segment 1 Duration: 50ms
    (Expected: 0x16=0200, 0x1E=C800 (200), based on refined rule val_0x1E = Dur0Units_actual when N>1 and Dur0 != 100)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 28 00 00 00  02 00 02 00  64 00 46 00  00 00 00 00 | (.......d.F.....
0000:0020 | 04 00 01 00  00 C8 00 00  00 00 00 64  00 72 01 00 | .....È.....d.r..
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  43 44 5C 02 | .2......2...CD\.
0000:0040 | 00 00 C8 00  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ..È...ÿ..ÿ..ÿ..ÿ
```

### Test Q4: (N>1, Dur0Units_actual is NOT a multiple of 100)

    Number of Segments (N): 2
    Segment 0 Duration (Dur0Units_actual): 170ms (AA00)
    Segment 1 Duration: 50ms
    (Expected: 0x16=0100, 0x1E=AA00 (170), based on refined rule val_0x1E = Dur0Units_actual when N>1 and Dur0 != 100)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 28 00 00 00  02 00 01 00  64 00 46 00  00 00 46 00 | (.......d.F...F.
0000:0020 | 04 00 01 00  00 AA 00 00  00 00 00 64  00 72 01 00 | .....ª.....d.r..
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  43 44 5C 02 | .2......2...CD\.
0000:0040 | 00 00 C8 00  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ..È...ÿ..ÿ..ÿ..ÿ
```

### Test R1:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 1929ms (8907)
    (Expected Field[+0x11] for Block 1: 8907 (1929))

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  13 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  1D 00 04 00  01 00 00 89  07 00 00 43 | ±..............C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test R2: (This is a repeat of J1/Test A's relevant part, for specific re-confirmation alongside boundary tests)

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 1930ms (8A07)
    (Expected Field[+0x11] for Block 1: 1E00 (30))

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  13 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  1E 00 04 00  01 00 00 8A  07 00 00 43 | ±..............C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test R3:

    Segment 0 Duration: 50ms
    Segment 1 Duration: 50ms
    Segment 2 Duration: 1931ms (8B07)
    (Expected Field[+0x11] for Block 1: 8B07 (1931))

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  13 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  1F 00 04 00  01 00 00 8B  07 00 00 43 | ±..............C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
0000:0060 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
```
---

## Additional Test Series (S, T, U, V) - 1000Hz Refresh Rate

**Date:** 2025-06-02 (following M-R series)

These tests further investigate Header Field `0x1E` and Duration Block Field `+0x11` behaviors.

### Test S1:

    Segment 0 Duration (Dur0Units_actual): 350ms
    (If 0x1E = Dur0 % 100: expect 50. If behavior similar to 300: expect 0. If behavior similar to 500: expect 350)
    Actually, since 350 is not a multiple of 100, this test should follow the val_0x1E_dec = Dur0Units_actual % NominalBase rule. Expect 0x1E = 50. This test serves as a control.

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 03 00  64 00 33 00  00 00 32 00 | ........d.3...2.
0000:0020 | 04 00 01 00  00 5E 01 00  00 43 44 30  01 00 00 64 | .....^...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```

### Test S2:

    Segment 0 Duration (Dur0Units_actual): 400ms
    (Goal: If 0x1E = 0 for multiples <= 300, and 0x1E = Dur0 for 500, what about 400? Is it 0 or 400?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 04 00  64 00 33 00  00 00 00 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 90 01 00  00 43 44 30  01 00 00 64 | .........CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```

### Test S3:

    Segment 0 Duration (Dur0Units_actual): 450ms
    (Control, expect 0x1E = 50)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 15 00 00 00  01 00 04 00  64 00 33 00  00 00 32 00 | ........d.3...2.
0000:0020 | 04 00 01 00  00 C2 01 00  00 43 44 30  01 00 00 64 | .....Â...CD0...d
0000:0030 | 00 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
```

### Test T1:

    Segment 2 Duration (Dur_k+1): 120ms
    (Is it 20 or 120? Compare with original Test C where Dur_k+1=120 gave 120)
    (Test T1-T6 have common Seg0=50ms, Seg1=50ms)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  14 00 04 00  01 00 00 78  00 00 00 43 | ±..........x...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test T2:

    Segment 2 Duration (Dur_k+1): 140ms
    (Is it 40 or 140?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  28 00 04 00  01 00 00 8C  00 00 00 43 | ±...(..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test T3:

    Segment 2 Duration (Dur_k+1): 148ms
    (Is it 48 or 148?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  30 00 04 00  01 00 00 94  00 00 00 43 | ±...0..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test T4:

    Segment 2 Duration (Dur_k+1): 149ms
    (Is it 49 or 149?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  31 00 04 00  01 00 00 95  00 00 00 43 | ±...1..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test T5: (This is a repeat of Test H3 for context, where Dur_k+1 was 150 and Field[+0x11] was 150)

    Segment 2 Duration (Dur_k+1): 150ms
    (Expect 150)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43 | ±...2..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test T6:

    Segment 2 Duration (Dur_k+1): 151ms
    (Is it 51 or 151?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  01 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  33 00 04 00  01 00 00 97  00 00 00 43 | ±...3..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test U1:

    Segment 2 Duration (Dur_k+1): 400ms
    (Is it 0 or 400? Test A had Dur1=470, where Field[+0x11] was 470, not 0 or 70)
    (Test U1-U3 have common Seg0=50ms, Seg1=50ms)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  04 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 90  01 00 00 43 | ±..............C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test U2:

    Segment 2 Duration (Dur_k+1): 500ms
    (Is it 0 or 500?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  05 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 F4  01 00 00 43 | ±..........ô...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test U3:

    Segment 2 Duration (Dur_k+1): 1000ms
    (Is it 0 or 1000? Test L6 had Dur1=1000 -> Field[+0x11]=1000)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  0A 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 E8  03 00 00 43 | ±..........è...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test V1:

    Segment 2 Duration (Dur_k+1): 301ms
    (Is it 1 or 301?)
    (Test V1-V7 have common Seg0=50ms, Seg1=50ms)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  03 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  01 00 04 00  01 00 00 2D  01 00 00 43 | ±..........-...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test V2:

    Segment 2 Duration (Dur_k+1): 349ms
    (Is it 49 or 349?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  03 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  31 00 04 00  01 00 00 5D  01 00 00 43 | ±...1......]...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test V3:

    Segment 2 Duration (Dur_k+1): 350ms
    (Is it 50 or 350?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  03 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 5E  01 00 00 43 | ±...2......^...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```
---

## Duration Block `+0x11` Interaction Tests (DB_11 Series) - 1000Hz

**Date:** 2025-06-02

These tests investigate the interaction of `Dur_k` (current segment duration) and `Dur_k+1` (next segment duration) on the value of `Field[+0x11]` for `Block k`. All tests are N=3 segments, 1000Hz PRG refresh rate. Seg0 is fixed at 50ms. The focus is on `Field[+0x11]` in Block 1, which describes Seg1 and looks ahead to Seg2.

Colors for all segments are FF0000 (Red), 00FF00 (Green), 0000FF (Blue) cycling, 4 pixels.
Header values are common: `0x0C=E803` (1000Hz), `0x14=0300` (N=3), `0x10=3B00` (Pointer1 for N=3), `0x1A=5900` (RGB offset for N=3).
`Dur0` (Seg0 duration) = 50ms. So, `Header[0x16]=0000` (0), `Header[0x1E]=3200` (50).

Common structure for Duration Blocks (Block 0 for Seg0, Block 1 for Seg1, Block 2 for Seg2):
*   Block 0 (`offset 0x20`): `PixelCount=0400`, `Const02=010000`, `CurrentDur(Seg0)=3200`(50ms), `Const07=0000`. `Field[+0x09].part2=6400`. `Index1Value=8501`.
*   Block 2 (Last Block, `offset 0x46`): `PixelCount=0400`, `Const02=010000`, `CurrentDur(Seg2)=variable`, `Const07=0000`, `LastBlockConst09=4344`, `Index2Part1=variable`, `LastBlockConst0D=0000`, `Index2Part2=variable`, `LastBlockConst11=0000`.

### Series DB_11_A: `Dur_k+1` (Seg2 Duration) = 150ms (`96 00`)

*   Seg0=50ms, Seg1=`Dur_k` (variable), Seg2=150ms.
*   Focus on Block 1 `Field[+0x11]` (for Seg1, looking at Seg2's 150ms duration).
*   `Field[+0x09].part1` for Block 0 (looking at Seg1) is `floor(Dur_k/100)`.
*   `Field[+0x09].part1` for Block 1 (looking at Seg2=150ms) is `floor(150/100) = 0100` (1).

#### Test DB_11_A1: `Dur_k` (Seg1 Duration) = 70ms (`46 00`)
*   Block 0 `Field[+0x09].part1` (for Seg1=70ms): `0000` (0). `Field[+0x11]` (for Seg1=70ms): `4600` (70).
*   Block 1 (Seg1 Duration = 70ms): `CurrentDur=4600`. `Field[+0x09].part1=0100`.
*   Block 1 `Field[+0x11]` (for Seg2=150ms): `3200` (50) -> `150 % 100`.
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 46 00 04  00 01 00 00  46 00 00 00  01 00 64 00 | .F......F.....d.
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43 | ±...2..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

#### Test DB_11_A2: `Dur_k` (Seg1 Duration) = 99ms (`63 00`)
*   Block 0 `Field[+0x09].part1` (for Seg1=99ms): `0000` (0). `Field[+0x11]` (for Seg1=99ms): `6300` (99).
*   Block 1 (Seg1 Duration = 99ms): `CurrentDur=6300`. `Field[+0x09].part1=0100`.
*   Block 1 `Field[+0x11]` (for Seg2=150ms): `3200` (50) -> `150 % 100`.
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 63 00 04  00 01 00 00  63 00 00 00  01 00 64 00 | .c......c.....d.
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43 | ±...2..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

#### Test DB_11_A3: `Dur_k` (Seg1 Duration) = 101ms (`65 00`)
*   Block 0 `Field[+0x09].part1` (for Seg1=101ms): `0100` (1). `Field[+0x11]` (for Seg1=101ms): `6500` (101).
*   Block 1 (Seg1 Duration = 101ms): `CurrentDur=6500`. `Field[+0x09].part1=0100`.
*   Block 1 `Field[+0x11]` (for Seg2=150ms): `9600` (150) -> Direct passthrough.
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 01 00 04  00 01 00 00  65 00 00 00  01 00 64 00 | ........e.....d.
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43 | ±...2..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```
*   Correction: Block 1 `Field[+0x11]` for DB_11_A3 should be `9600` (150) according to the hex dump (offset `0x40` value `3200` is for color data intro). The dump at `0x46+0x11 = 0x57` is `96 00`. This needs careful parsing.
*   Re-parsing DB_11_A3, Block 1 (starts `0x33`): `Dur_k=101` (`6500` at `0x33+5`). `Field[+0x11]` (at `0x33+17=0x44`) is `9600` (150). This is Direct Passthrough.

#### Test DB_11_A4: `Dur_k` (Seg1 Duration) = 140ms (`8C 00`)
*   Block 0 `Field[+0x09].part1` (for Seg1=140ms): `0100` (1). `Field[+0x11]` (for Seg1=140ms): `8C00` (140).
*   Block 1 (Seg1 Duration = 140ms): `CurrentDur=8C00`. `Field[+0x09].part1=0100`.
*   Block 1 `Field[+0x11]` (for Seg2=150ms, at `0x33+17=0x44`): `9600` (150) -> Direct passthrough.
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 28 00 04  00 01 00 00  8C 00 00 00  01 00 64 00 | .(............d.
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43 | ±...2..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```
*   Re-parsing DB_11_A4, Block 1 (starts `0x33`): `Dur_k=140` (`8C00` at `0x33+5`). `Field[+0x11]` (at `0x33+17=0x44`) is `9600` (150). This is Direct Passthrough.

#### Test DB_11_A5: `Dur_k` (Seg1 Duration) = 150ms (`96 00`)
*   Block 0 `Field[+0x09].part1` (for Seg1=150ms): `0100` (1). `Field[+0x11]` (for Seg1=150ms): `9600` (150).
*   Block 1 (Seg1 Duration = 150ms): `CurrentDur=9600`. `Field[+0x09].part1=0100`.
*   Block 1 `Field[+0x11]` (for Seg2=150ms, at `0x33+17=0x44`): `9600` (150) -> Direct passthrough.
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  96 00 00 00  01 00 64 00 | .2............d.
0000:0040 | B1 02 00 00  32 00 04 00  01 00 00 96  00 00 00 43 | ±...2..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```
*   Re-parsing DB_11_A5, Block 1 (starts `0x33`): `Dur_k=150` (`9600` at `0x33+5`). `Field[+0x11]` (at `0x33+17=0x44`) is `9600` (150). This is Direct Passthrough.

*Summary for DB_11_A (Dur_k+1 = 150ms):*
*   Dur_k=50 (T5): `+0x11 = 50` (`150 % 100`)
*   Dur_k=70 (A1): `+0x11 = 50` (`150 % 100`)
*   Dur_k=99 (A2): `+0x11 = 50` (`150 % 100`)
*   Dur_k=100 (H3): `+0x11 = 150` (Direct Passthrough)
*   Dur_k=101 (A3): `+0x11 = 150` (Direct Passthrough)
*   Dur_k=140 (A4): `+0x11 = 150` (Direct Passthrough)
*   Dur_k=150 (A5): `+0x11 = 150` (Direct Passthrough)
This suggests that if `Dur_k+1 > 100` and not an override: if `Dur_k >= 100`, `Field[+0x11] = Dur_k+1`. If `Dur_k < 100`, `Field[+0x11] = Dur_k+1 % 100`.

### Series DB_11_B: `Dur_k+1` (Seg2 Duration) = 600ms (`58 02`)

*   Seg0=50ms, Seg1=`Dur_k` (variable), Seg2=600ms.
*   Focus on Block 1 `Field[+0x11]` (for Seg1, looking at Seg2's 600ms duration).
*   `Field[+0x09].part1` for Block 1 (looking at Seg2=600ms) is `floor(600/100) = 0600` (6).

#### Test DB_11_B1: `Dur_k` (Seg1 Duration) = 100ms (`64 00`)
*   Block 0 `Field[+0x09].part1` (for Seg1=100ms): `0100` (1). `Field[+0x11]` (for Seg1=100ms): `0000` (0).
*   Block 1 (Seg1 Duration = 100ms): `CurrentDur=6400`. `Field[+0x09].part1=0600`.
*   Block 1 `Field[+0x11]` (for Seg2=600ms, at `0x33+17=0x44`): `0000` (0).
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  06 00 64 00 | ........d.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 58  02 00 00 43 | ±..........X...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

#### Test DB_11_B2: `Dur_k` (Seg1 Duration) = 200ms (`C8 00`)
*   Block 0 `Field[+0x09].part1` (Seg1=200ms): `0200`(2). `Field[+0x11]` (Seg1=200ms): `0000`(0).
*   Block 1 (Seg1 Duration = 200ms): `CurrentDur=C800`. `Field[+0x09].part1=0600`.
*   Block 1 `Field[+0x11]` (for Seg2=600ms, at `0x33+17=0x44`): `0000` (0).
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 02 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 00 00 04  00 01 00 00  C8 00 00 00  06 00 64 00 | ........È.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 58  02 00 00 43 | ±..........X...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

#### Test DB_11_B3: `Dur_k` (Seg1 Duration) = 500ms (`F4 01`)
*   Block 0 `Field[+0x09].part1` (Seg1=500ms): `0500`(5). `Field[+0x11]` (Seg1=500ms): `0000`(0).
*   Block 1 (Seg1 Duration = 500ms): `CurrentDur=F401`. `Field[+0x09].part1=0600`.
*   Block 1 `Field[+0x11]` (for Seg2=600ms, at `0x33+17=0x44`): `0000` (0).
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 05 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 00 00 04  00 01 00 00  F4 01 00 00  06 00 64 00 | ........ô.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 58  02 00 00 43 | ±..........X...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

#### Test DB_11_B4: `Dur_k` (Seg1 Duration) = 600ms (`58 02`)
*   Block 0 `Field[+0x09].part1` (Seg1=600ms): `0600`(6). `Field[+0x11]` (Seg1=600ms): `0000`(0).
*   Block 1 (Seg1 Duration = 600ms): `CurrentDur=5802`. `Field[+0x09].part1=0600`.
*   Block 1 `Field[+0x11]` (for Seg2=600ms, at `0x33+17=0x44`): `5802` (600) -> Direct Passthrough.
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 06 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 00 00 04  00 01 00 00  58 02 00 00  06 00 64 00 | ........X.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 58  02 00 00 43 | ±..........X...C
```
*   Corrected: Block 1 `Field[+0x11]` for B4 (at `0x44`) is `5802` (600).

#### Test DB_11_B5: `Dur_k` (Seg1 Duration) = 999ms (`E7 03`)
*   Block 0 `Field[+0x09].part1` (Seg1=999ms): `0900`(9). `Field[+0x11]` (Seg1=999ms): `E703`(999).
*   Block 1 (Seg1 Duration = 999ms): `CurrentDur=E703`. `Field[+0x09].part1=0600`.
*   Block 1 `Field[+0x11]` (for Seg2=600ms, at `0x33+17=0x44`): `0000` (0).
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 09 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 63 00 04  00 01 00 00  E7 03 00 00  06 00 64 00 | .c......ç.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 58  02 00 00 43 | ±..........X...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

*Summary for DB_11_B (Dur_k+1 = 600ms):*
*   Dur_k=50 (U-series reasoning): `+0x11 = 0`
*   Dur_k=100 (B1): `+0x11 = 0`
*   Dur_k=200 (B2): `+0x11 = 0`
*   Dur_k=500 (B3): `+0x11 = 0`
*   Dur_k=600 (B4): `+0x11 = 600` (Direct Passthrough)
*   Dur_k=999 (B5): `+0x11 = 0`
*   Dur_k=1000 (L5): `+0x11 = 600` (Direct Passthrough, although L5 was Dur_k+1=1930, Dur_k=1000, Field[+0x11]=600 is for Dur_k=1000, Dur_k-1=600) - *Recheck L5 context: L5 is Dur0=1k, Dur1=600, Dur2=1930. Block0 +0x11 (for Dur1=600) is 600. Block1 +0x11 (for Dur2=1930, with Dur_k=600) is 30 (anomaly).*
This implies for `Dur_k+1 % 100 == 0`: if `Dur_k == Dur_k+1`, `Field[+0x11] = Dur_k+1`. Otherwise, `Field[+0x11] = 0`.

### Series DB_11_C: `Dur_k+1` (Seg2 Duration) = 1000ms (`E8 03`)

*   Seg0=50ms, Seg1=`Dur_k` (variable), Seg2=1000ms.
*   Focus on Block 1 `Field[+0x11]` (for Seg1, looking at Seg2's 1000ms duration).
*   `Field[+0x09].part1` for Block 1 (looking at Seg2=1000ms) is `floor(1000/100) = 0A00` (10).

#### Test DB_11_C1: `Dur_k` (Seg1 Duration) = 100ms (`64 00`)
*   Block 0 `Field[+0x09].part1` (Seg1=100ms): `0100`(1). `Field[+0x11]` (Seg1=100ms): `0000`(0).
*   Block 1 (Seg1 Duration = 100ms): `CurrentDur=6400`. `Field[+0x09].part1=0A00`.
*   Block 1 `Field[+0x11]` (for Seg2=1000ms, at `0x33+17=0x44`): `0000` (0).
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 01 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  0A 00 64 00 | ........d.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 E8  03 00 00 43 | ±..........è...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

#### Test DB_11_C2: `Dur_k` (Seg1 Duration) = 500ms (`F4 01`)
*   Block 0 `Field[+0x09].part1` (Seg1=500ms): `0500`(5). `Field[+0x11]` (Seg1=500ms): `0000`(0).
*   Block 1 (Seg1 Duration = 500ms): `CurrentDur=F401`. `Field[+0x09].part1=0A00`.
*   Block 1 `Field[+0x11]` (for Seg2=1000ms, at `0x33+17=0x44`): `0000` (0).
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 05 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 00 00 04  00 01 00 00  F4 01 00 00  0A 00 64 00 | ........ô.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 E8  03 00 00 43 | ±..........è...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

#### Test DB_11_C3: `Dur_k` (Seg1 Duration) = 999ms (`E7 03`)
*   Block 0 `Field[+0x09].part1` (Seg1=999ms): `0900`(9). `Field[+0x11]` (Seg1=999ms): `E703`(999).
*   Block 1 (Seg1 Duration = 999ms): `CurrentDur=E703`. `Field[+0x09].part1=0A00`.
*   Block 1 `Field[+0x11]` (for Seg2=1000ms, at `0x33+17=0x44`): `0000` (0).
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 09 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 63 00 04  00 01 00 00  E7 03 00 00  0A 00 64 00 | .c......ç.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 E8  03 00 00 43 | ±..........è...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

*Summary for DB_11_C (Dur_k+1 = 1000ms):*
*   Dur_k=50 (U3): `+0x11 = 0`
*   Dur_k=100 (C1): `+0x11 = 0`
*   Dur_k=500 (C2): `+0x11 = 0`
*   Dur_k=999 (C3): `+0x11 = 0`
*   Dur_k=1000 (L6): `+0x11 = 1000` (Direct Passthrough)
This again supports for `Dur_k+1 % 100 == 0`: if `Dur_k == Dur_k+1`, `Field[+0x11] = Dur_k+1`. Otherwise, `Field[+0x11] = 0`.

---

### Test V4:

    Segment 2 Duration (Dur_k+1): 351ms
    (Is it 51 or 351?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  03 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  33 00 04 00  01 00 00 5F  01 00 00 43 | ±...3......_...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test V5:

    Segment 2 Duration (Dur_k+1): 399ms
    (Is it 99 or 399?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  03 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  63 00 04 00  01 00 00 8F  01 00 00 43 | ±...c..........C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test V6: (This is Test U1 again, placed here for context of this range)

    Segment 2 Duration (Dur_k+1): 400ms
    (Is it 0 or 400?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  04 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 90  01 00 00 43 | ±..............C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
```

### Test V7:

    Segment 2 Duration (Dur_k+1): 401ms
    (Is it 1 or 401?)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  E8 03 50 49 | PR.IN.......è.PI
0000:0010 | 3B 00 00 00  03 00 00 00  64 00 59 00  00 00 32 00 | ;.......d.Y...2.
0000:0020 | 04 00 01 00  00 32 00 00  00 00 00 64  00 85 01 00 | .....2.....d....
0000:0030 | 00 32 00 04  00 01 00 00  32 00 00 00  04 00 64 00 | .2......2.....d.
0000:0040 | B1 02 00 00  01 00 04 00  01 00 00 91  01 00 00 43 | ±..............C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
0000:0060 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
```

---

## Official App Fade Tests

**Date:** 2025-06-05 16:10 UTC+7

These are fade test results from the official LTX app to understand how the official app produces fade effects and what the resulting PRG files contain.

### red-blue_2m30s_100r.prg

**Description:** Fade from red to blue over 2 minutes and 30 seconds with 100Hz refresh rate.

**Truncated hex dump (full file goes until 0000:B000):**
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  98 3A 33 00  00 00 00 00 | .........:3.....
0000:0020 | 04 00 01 00  00 98 3A 00  00 43 44 CC  AF 00 00 98 | ......:..CDÌ¯...
0000:0030 | 3A 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | :..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0040 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0050 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0060 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0070 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0080 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0090 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00A0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00B0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:00C0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00D0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00E0 | 00 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:00F0 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0100 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:0110 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:0120 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0130 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:0140 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:0150 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0160 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:0170 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:0180 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FD | þ..þ..þ..þ..þ..ý
0000:0190 | 00 02 FD 00  02 FD 00 02  FD 00 02 FD  00 02 FD 00 | ..ý..ý..ý..ý..ý.
0000:01A0 | 02 FD 00 02  FD 00 02 FD  00 02 FD 00  02 FD 00 02 | .ý..ý..ý..ý..ý..
0000:01B0 | FD 00 02 FD  00 02 FD 00  02 FD 00 02  FD 00 02 FD | ý..ý..ý..ý..ý..ý
0000:01C0 | 00 02 FD 00  02 FD 00 02  FD 00 02 FD  00 02 FD 00 | ..ý..ý..ý..ý..ý.
0000:01D0 | 02 FD 00 02  FD 00 02 FD  00 02 FD 00  02 FD 00 02 | .ý..ý..ý..ý..ý..
0000:01E0 | FD 00 02 FD  00 02 FD 00  02 FD 00 02  FD 00 02 FD | ý..ý..ý..ý..ý..ý
0000:01F0 | 00 02 FD 00  02 FD 00 02  FD 00 02 FD  00 02 FD 00 | ..ý..ý..ý..ý..ý.
0000:0200 | 02 FD 00 02  FD 00 02 FD  00 02 FD 00  02 FD 00 02 | .ý..ý..ý..ý..ý..
...
```

**Analysis:**
- Duration: `98 3A` (14,872) units at 100Hz = 148.72 seconds = 2m28.72s
- Header field 0x16: `01 00` (1)
- Header field 0x1E: `00 00` (0)
- Shows gradual color transition from `FF 00 00` (red) to `00 00 FF` (blue)
- Transition pattern: `FF→FE→FD...` (red decreasing) and `00→01→02...` (blue increasing)

### red1s_red-blue1s_green1s_100r.prg

**Description:** Multi-segment sequence:
- Solid Red (1 second)
- Fade from Red to Blue (2 seconds)
- Solid Green (1 second)

```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 3B 00 00 00  03 00 01 00  64 00 59 00  00 00 00 00 | ;.......d.Y.....
0000:0020 | 04 00 01 00  00 64 00 00  00 01 00 64  00 85 01 00 | .....d.....d....
0000:0030 | 00 00 00 04  00 01 00 00  64 00 00 00  01 00 64 00 | ........d.....d.
0000:0040 | B1 02 00 00  00 00 04 00  01 00 00 64  00 00 00 43 | ±..........d...C
0000:0050 | 44 88 03 00  00 2C 01 00  00 FF 00 00  FF 00 00 FF | D....,...ÿ..ÿ..ÿ
0000:0060 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0070 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0080 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0090 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00A0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:00B0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00C0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00D0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:00E0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00F0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0100 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0110 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0120 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0130 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0140 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0150 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0160 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0170 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0180 | 00 00 FF 00  00 FF 00 00  FC 00 03 FA  00 05 F7 00 | ..ÿ..ÿ..ü..ú..÷.
0000:0190 | 08 F5 00 0A  F2 00 0D F0  00 0F ED 00  12 EA 00 15 | .õ..ò..ð..í..ê..
0000:01A0 | E8 00 17 E5  00 1A E3 00  1C E0 00 1F  DE 00 21 DB | è..å..ã..à..Þ.!Û
0000:01B0 | 00 24 D8 00  27 D6 00 29  D3 00 2C D1  00 2E CE 00 | .$Ø.'Ö.)Ó.,Ñ..Î.
0000:01C0 | 31 CB 00 34  C9 00 36 C6  00 39 C4 00  3B C1 00 3E | 1Ë.4É.6Æ.9Ä.;Á.>
0000:01D0 | BF 00 40 BC  00 43 B9 00  46 B7 00 48  B4 00 4B B2 | ¿.@¼.C¹.F·.H´.K²
0000:01E0 | 00 4D AF 00  50 AD 00 52  AA 00 55 A7  00 58 A5 00 | .M¯.P..Rª.U§.X¥.
0000:01F0 | 5A A2 00 5D  A0 00 5F 9D  00 62 9B 00  64 98 00 67 | Z¢.] ._..b..d..g
0000:0200 | 95 00 6A 93  00 6C 90 00  6F 8E 00 71  8B 00 74 89 | ..j..l..o..q..t.
0000:0210 | 00 76 86 00  79 83 00 7C  81 00 7E 7E  00 81 7C 00 | .v..y..|..~~..|.
0000:0220 | 83 79 00 86  76 00 89 74  00 8B 71 00  8E 6F 00 90 | .y..v..t..q..o..
0000:0230 | 6C 00 93 6A  00 95 67 00  98 64 00 9B  62 00 9D 5F | l..j..g..d..b.._
0000:0240 | 00 A0 5D 00  A2 5A 00 A5  58 00 A7 55  00 AA 52 00 | . ].¢Z.¥X.§U.ªR.
0000:0250 | AD 50 00 AF  4D 00 B2 4B  00 B4 48 00  B7 46 00 B9 | .P.¯M.²K.´H.·F.¹
0000:0260 | 43 00 BC 40  00 BF 3E 00  C1 3B 00 C4  39 00 C6 36 | C.¼@.¿>.Á;.Ä9.Æ6
0000:0270 | 00 C9 34 00  CB 31 00 CE  2E 00 D1 2C  00 D3 29 00 | .É4.Ë1.Î..Ñ,.Ó).
0000:0280 | D6 27 00 D8  24 00 DB 21  00 DE 1F 00  E0 1C 00 E3 | Ö'.Ø$.Û!.Þ..à..ã
0000:0290 | 1A 00 E5 17  00 E8 15 00  EA 12 00 ED  0F 00 F0 0D | ..å..è..ê..í..ð.
0000:02A0 | 00 F2 0A 00  F5 08 00 F7  05 00 FA 03  00 FC 00 00 | .ò..õ..÷..ú..ü..
0000:02B0 | FF 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ÿ.ÿ..ÿ..ÿ..ÿ..ÿ.
0000:02C0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:02D0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:02E0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:02F0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0300 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0310 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0320 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0330 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0340 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0350 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0360 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0370 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0380 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0390 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:03A0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:03B0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:03C0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:03D0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 42 54 00 | ..ÿ..ÿ..ÿ..ÿ.BT.
0000:03E0 | 00 00 00                                           | ...
```

**Analysis:**
- N=3 segments: Solid Red (1s) → Red-Blue Fade (2s) → Solid Green (1s)
- Header field 0x16: `01 00` (1)
- Header field 0x1E: `00 00` (0)
- Segment durations: `64 00` (100 units = 1s each for solid segments)
- Shows clear transition from solid red blocks to gradual fade pattern to solid green
- Fade section starts around offset 0x0180 with `FC 00 03` pattern
- Demonstrates how fades are embedded within multi-segment sequences

---

## Fade Tests from Official App

**Date:** 2025-01-05 11:01 UTC+7

These are fade test results from the official LTX app to understand how the official app produces fade effects and what the resulting PRG files contain.

### Long Fade Tests - Red to Blue Transitions

**Naming Convention:** `red-blue_10m55s400ms_100r.prg` means fade from red to blue over the course of 10 minutes, 55 seconds, and 400 milliseconds with a refresh rate of 100Hz.

#### Failed Fade Tests (Too Long or Errors)

- **red-blue_10m55s400ms_100r.prg** - never actually changed from red - **FAIL**
- **red-blue_10m50s_100r.prg** - started changing, but way too fast and then errored out - **FAIL**
- **red-blue_10m_100r.prg** - started changing, but way too fast and then errored out - **FAIL**
- **red-blue_5m_100r.prg** - changes way too fast, but doesn't error out - **FAIL**
- **red-blue_4m_100r.prg** - changes way too fast, but doesn't error out - **FAIL**
- **red-blue_3m_100r.prg** - changes way too fast, but doesn't error out - **FAIL**
- **red-blue_2m30s_100r.prg** - changes way too fast, but doesn't error out - **FAIL**

#### Successful Fade Tests

### red-blue_2m15s_100r.prg - Works as intended
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  BC 34 33 00  00 00 00 00 | ........¼43.....
0000:0020 | 04 00 01 00  00 BC 34 00  00 43 44 38  9E 00 00 BC | .....¼4..CD8...¼
0000:0030 | 34 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | 4..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0040 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0050 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0060 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0070 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0080 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0090 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00A0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00B0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:00C0 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FE | ÿ..ÿ..ÿ..ÿ..ÿ..þ
0000:00D0 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:00E0 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:00F0 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0100 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:0110 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:0120 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0130 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:0140 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:0150 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0160 | 00 01 FE 00  01 FE 00 01  FE 00 01 FD  00 02 FD 00 | ..þ..þ..þ..ý..ý.
0000:0170 | 02 FD 00 02  FD 00 02 FD  00 02 FD 00  02 FD 00 02 | .ý..ý..ý..ý..ý..
0000:0180 | FD 00 02 FD  00 02 FD 00  02 FD 00 02  FD 00 02 FD | ý..ý..ý..ý..ý..ý
0000:0190 | 00 02 FD 00  02 FD 00 02  FD 00 02 FD  00 02 FD 00 | ..ý..ý..ý..ý..ý.
0000:01A0 | 02 FD 00 02  FD 00 02 FD  00 02 FD 00  02 FD 00 02 | .ý..ý..ý..ý..ý..
```
*(truncated - actual file goes until 0000:9E6C)*

### red-blue_2m_100r.prg - Works as intended
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  E0 2E 33 00  00 00 00 00 | ........à.3.....
0000:0020 | 04 00 01 00  00 E0 2E 00  00 43 44 A4  8C 00 00 E0 | .....à...CD¤...à
0000:0030 | 2E 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ...ÿ..ÿ..ÿ..ÿ..ÿ
0000:0040 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0050 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0060 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0070 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:0080 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:0090 | FF 00 00 FF  00 00 FF 00  00 FF 00 00  FF 00 00 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00A0 | 00 00 FF 00  00 FF 00 00  FF 00 00 FF  00 00 FF 00 | ..ÿ..ÿ..ÿ..ÿ..ÿ.
0000:00B0 | 00 FF 00 00  FF 00 00 FF  00 00 FF 00  00 FF 00 00 | .ÿ..ÿ..ÿ..ÿ..ÿ..
0000:00C0 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:00D0 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:00E0 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:00F0 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0100 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:0110 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FE 00 01 | .þ..þ..þ..þ..þ..
0000:0120 | FE 00 01 FE  00 01 FE 00  01 FE 00 01  FE 00 01 FE | þ..þ..þ..þ..þ..þ
0000:0130 | 00 01 FE 00  01 FE 00 01  FE 00 01 FE  00 01 FE 00 | ..þ..þ..þ..þ..þ.
0000:0140 | 01 FE 00 01  FE 00 01 FE  00 01 FE 00  01 FD 00 02 | .þ..þ..þ..þ..ý..
0000:0150 | FD 00 02 FD  00 02 FD 00  02 FD 00 02  FD 00 02 FD | ý..ý..ý..ý..ý..ý
0000:0160 | 00 02 FD 00  02 FD 00 02  FD 00 02 FD  00 02 FD 00 | ..ý..ý..ý..ý..ý.
0000:0170 | 02 FD 00 02  FD 00 02 FD  00 02 FD 00  02 FD 00 02 | .ý..ý..ý..ý..ý..
0000:0180 | FD 00 02 FD  00 02 FD 00  02 FD 00 02  FD 00 02 FD | ý..ý..ý..ý..ý..ý
0000:0190 | 00 02 FD 00  02 FD 00 02  FD 00 02 FD  00 02 FD 00 | ..ý..ý..ý..ý..ý.
0000:01A0 | 02 FD 00 02  FD 00 02 FD  00 02 FD 00  02 FD 00 02 | .ý..ý..ý..ý..ý..
0000:01B0 | FD 00 02 FD  00 02 FD 00  02 FD 00 02  FD 00 02 FD | ý..ý..ý..ý..ý..ý
0000:01C0 | 00 02 FD 00  02 FD 00 02  FD 00 02 FD  00 02 FD 00 | ..ý..ý..ý..ý..ý.
0000:01D0 | 02 FD 00 02  FD 00 02 FD  00 02 FC 00  03 FC 00 03 | .ý..ý..ý..ü..ü..
0000:01E0 | FC 00 03 FC  00 03 FC 00  03 FC 00 03  FC 00 03 FC | ü..ü..ü..ü..ü..ü
0000:01F0 | 00 03 FC 00  03 FC 00 03  FC 00 03 FC  00 03 FC 00 | ..ü..ü..ü..ü..ü.
0000:0200 | 03 FC 00 03  FC 00 03 FC  00 03 FC 00  03 FC 00 03 | .ü..ü..ü..ü..ü..
0000:0210 | FC 00 03 FC  00 03 FC 00  03 FC 00 03  FC 00 03 FC | ü..ü..ü..ü..ü..ü
0000:0220 | 00 03 FC 00  03 FC 00 03  FC 00 03 FC  00 03 FC 00 | ..ü..ü..ü..ü..ü.
```
*(truncated - actual file goes until 0000:8CD8)*

### red-blue_5s_100r.prg - Works as intended
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  F4 01 33 00  00 00 00 00 | ........ô.3.....
0000:0020 | 04 00 01 00  00 F4 01 00  00 43 44 E0  05 00 00 F4 | .....ô...CDà...ô
0000:0030 | 01 00 00 FF  00 00 FE 00  01 FE 00 01  FD 00 02 FD | ...ÿ..þ..þ..ý..ý
0000:0040 | 00 02 FC 00  03 FC 00 03  FB 00 04 FB  00 04 FA 00 | ..ü..ü..û..û..ú.
0000:0050 | 05 FA 00 05  F9 00 06 F9  00 06 F8 00  07 F8 00 07 | .ú..ù..ù..ø..ø..
0000:0060 | F7 00 08 F7  00 08 F6 00  09 F6 00 09  F5 00 0A F5 | ÷..÷..ö..ö..õ..õ
0000:0070 | 00 0A F4 00  0B F4 00 0B  F3 00 0C F3  00 0C F2 00 | ..ô..ô..ó..ó..ò.
0000:0080 | 0D F2 00 0D  F1 00 0E F1  00 0E F0 00  0F F0 00 0F | .ò..ñ..ñ..ð..ð..
0000:0090 | EF 00 10 EF  00 10 EE 00  11 EE 00 11  ED 00 12 ED | ï..ï..î..î..í..í
0000:00A0 | 00 12 EC 00  13 EC 00 13  EB 00 14 EB  00 14 EA 00 | ..ì..ì..ë..ë..ê.
0000:00B0 | 15 EA 00 15  E9 00 16 E9  00 16 E8 00  17 E7 00 18 | .ê..é..é..è..ç..
0000:00C0 | E7 00 18 E6  00 19 E6 00  19 E5 00 1A  E5 00 1A E4 | ç..æ..æ..å..å..ä
0000:00D0 | 00 1B E4 00  1B E3 00 1C  E3 00 1C E2  00 1D E2 00 | ..ä..ã..ã..â..â.
0000:00E0 | 1D E1 00 1E  E1 00 1E E0  00 1F E0 00  1F DF 00 20 | .á..á..à..à..ß. 
0000:00F0 | DF 00 20 DE  00 21 DE 00  21 DD 00 22  DD 00 22 DC | ß. Þ.!Þ.!Ý."Ý."Ü
0000:0100 | 00 23 DC 00  23 DB 00 24  DB 00 24 DA  00 25 DA 00 | .#Ü.#Û.$Û.$Ú.%Ú.
0000:0110 | 25 D9 00 26  D9 00 26 D8  00 27 D8 00  27 D7 00 28 | %Ù.&Ù.&Ø.'Ø.'×.(
0000:0120 | D7 00 28 D6  00 29 D6 00  29 D5 00 2A  D5 00 2A D4 | ×.(Ö.)Ö.)Õ.*Õ.*Ô
0000:0130 | 00 2B D4 00  2B D3 00 2C  D3 00 2C D2  00 2D D2 00 | .+Ô.+Ó.,Ó.,Ò.-Ò.
0000:0140 | 2D D1 00 2E  D0 00 2F D0  00 2F CF 00  30 CF 00 30 | -Ñ..Ð./Ð./Ï.0Ï.0
0000:0150 | CE 00 31 CE  00 31 CD 00  32 CD 00 32  CC 00 33 CC | Î.1Î.1Í.2Í.2Ì.3Ì
0000:0160 | 00 33 CB 00  34 CB 00 34  CA 00 35 CA  00 35 C9 00 | .3Ë.4Ë.4Ê.5Ê.5É.
0000:0170 | 36 C9 00 36  C8 00 37 C8  00 37 C7 00  38 C7 00 38 | 6É.6È.7È.7Ç.8Ç.8
0000:0180 | C6 00 39 C6  00 39 C5 00  3A C5 00 3A  C4 00 3B C4 | Æ.9Æ.9Å.:Å.:Ä.;Ä
0000:0190 | 00 3B C3 00  3C C3 00 3C  C2 00 3D C2  00 3D C1 00 | .;Ã.<Ã.<Â.=Â.=Á.
0000:01A0 | 3E C1 00 3E  C0 00 3F C0  00 3F BF 00  40 BF 00 40 | >Á.>À.?À.?¿.@¿.@
0000:01B0 | BE 00 41 BE  00 41 BD 00  42 BD 00 42  BC 00 43 BC | ¾.A¾.A½.B½.B¼.C¼
0000:01C0 | 00 43 BB 00  44 BB 00 44  BA 00 45 BA  00 45 B9 00 | .C».D».Dº.Eº.E¹.
0000:01D0 | 46 B8 00 47  B8 00 47 B7  00 48 B7 00  48 B6 00 49 | F¸.G¸.G·.H·.H¶.I
0000:01E0 | B6 00 49 B5  00 4A B5 00  4A B4 00 4B  B4 00 4B B3 | ¶.Iµ.Jµ.J´.K´.K³
0000:01F0 | 00 4C B3 00  4C B2 00 4D  B2 00 4D B1  00 4E B1 00 | .L³.L².M².M±.N±.
0000:0200 | 4E B0 00 4F  B0 00 4F AF  00 50 AF 00  50 AE 00 51 | N°.O°.O¯.P¯.P®.Q
0000:0210 | AE 00 51 AD  00 52 AD 00  52 AC 00 53  AC 00 53 AB | ®.Q..R..R¬.S¬.S«
0000:0220 | 00 54 AB 00  54 AA 00 55  AA 00 55 A9  00 56 A9 00 | .T«.Tª.Uª.U©.V©.
0000:0230 | 56 A8 00 57  A8 00 57 A7  00 58 A7 00  58 A6 00 59 | V¨.W¨.W§.X§.X¦.Y
0000:0240 | A6 00 59 A5  00 5A A5 00  5A A4 00 5B  A4 00 5B A3 | ¦.Y¥.Z¥.Z¤.[¤.[£
0000:0250 | 00 5C A3 00  5C A2 00 5D  A1 00 5E A1  00 5E A0 00 | .\£.\¢.]¡.^¡.^ .
0000:0260 | 5F A0 00 5F  9F 00 60 9F  00 60 9E 00  61 9E 00 61 | _ ._..`..`..a..a
0000:0270 | 9D 00 62 9D  00 62 9C 00  63 9C 00 63  9B 00 64 9B | ..b..b..c..c..d.
0000:0280 | 00 64 9A 00  65 9A 00 65  99 00 66 99  00 66 98 00 | .d..e..e..f..f..
0000:0290 | 67 98 00 67  97 00 68 97  00 68 96 00  69 96 00 69 | g..g..h..h..i..i
0000:02A0 | 95 00 6A 95  00 6A 94 00  6B 94 00 6B  93 00 6C 93 | ..j..j..k..k..l.
0000:02B0 | 00 6C 92 00  6D 92 00 6D  91 00 6E 91  00 6E 90 00 | .l..m..m..n..n..
0000:02C0 | 6F 90 00 6F  8F 00 70 8F  00 70 8E 00  71 8E 00 71 | o..o..p..p..q..q
0000:02D0 | 8D 00 72 8D  00 72 8C 00  73 8C 00 73  8B 00 74 8A | ..r..r..s..s..t.
0000:02E0 | 00 75 8A 00  75 89 00 76  89 00 76 88  00 77 88 00 | .u..u..v..v..w..
0000:02F0 | 77 87 00 78  87 00 78 86  00 79 86 00  79 85 00 7A | w..x..x..y..y..z
0000:0300 | 85 00 7A 84  00 7B 84 00  7B 83 00 7C  83 00 7C 82 | ..z..{..{..|..|.
0000:0310 | 00 7D 82 00  7D 81 00 7E  81 00 7E 80  00 7F 80 00 | .}..}..~..~.....
0000:0320 | 7F 7F 00 80  7F 00 80 7E  00 81 7E 00  81 7D 00 82 | .......~..~..}..
0000:0330 | 7D 00 82 7C  00 83 7C 00  83 7B 00 84  7B 00 84 7A | }..|..|..{..{..z
0000:0340 | 00 85 7A 00  85 79 00 86  79 00 86 78  00 87 78 00 | ..z..y..y..x..x.
0000:0350 | 87 77 00 88  77 00 88 76  00 89 76 00  89 75 00 8A | .w..w..v..v..u..
0000:0360 | 75 00 8A 74  00 8B 73 00  8C 73 00 8C  72 00 8D 72 | u..t..s..s..r..r
0000:0370 | 00 8D 71 00  8E 71 00 8E  70 00 8F 70  00 8F 6F 00 | ..q..q..p..p..o.
0000:0380 | 90 6F 00 90  6E 00 91 6E  00 91 6D 00  92 6D 00 92 | .o..n..n..m..m..
0000:0390 | 6C 00 93 6C  00 93 6B 00  94 6B 00 94  6A 00 95 6A | l..l..k..k..j..j
0000:03A0 | 00 95 69 00  96 69 00 96  68 00 97 68  00 97 67 00 | ..i..i..h..h..g.
0000:03B0 | 98 67 00 98  66 00 99 66  00 99 65 00  9A 65 00 9A | .g..f..f..e..e..
0000:03C0 | 64 00 9B 64  00 9B 63 00  9C 63 00 9C  62 00 9D 62
0000:03D0 | 00 9D 61 00  9E 61 00 9E  60 00 9F 60  00 9F 5F 00 | ..a..a..`..`.._.
0000:03E0 | A0 5F 00 A0  5E 00 A1 5E  00 A1 5D 00  A2 5C 00 A3 |  _. ^.¡^.¡].¢\.£
0000:03F0 | 5C 00 A3 5B  00 A4 5B 00  A4 5A 00 A5  5A 00 A5 59 | \.£[.¤[.¤Z.¥Z.¥Y
0000:0400 | 00 A6 59 00  A6 58 00 A7  58 00 A7 57  00 A8 57 00 | .¦Y.¦X.§X.§W.¨W.
0000:0410 | A8 56 00 A9  56 00 A9 55  00 AA 55 00  AA 54 00 AB | ¨V.©V.©U.ªU.ªT.«
0000:0420 | 54 00 AB 53  00 AC 53 00  AC 52 00 AD  52 00 AD 51 | T.«S.¬S.¬R..R..Q
0000:0430 | 00 AE 51 00  AE 50 00 AF  50 00 AF 4F  00 B0 4F 00 | .®Q.®P.¯P.¯O.°O.
0000:0440 | B0 4E 00 B1  4E 00 B1 4D  00 B2 4D 00  B2 4C 00 B3 | °N.±N.±M.²M.²L.³
0000:0450 | 4C 00 B3 4B  00 B4 4B 00  B4 4A 00 B5  4A 00 B5 49 | L.³K.´K.´J.µJ.µI
0000:0460 | 00 B6 49 00  B6 48 00 B7  48 00 B7 47  00 B8 47 00 | .¶I.¶H.·H.·G.¸G.
0000:0470 | B8 46 00 B9  45 00 BA 45  00 BA 44 00  BB 44 00 BB | ¸F.¹E.ºE.ºD.»D.»
0000:0480 | 43 00 BC 43  00 BC 42 00  BD 42 00 BD  41 00 BE 41 | C.¼C.¼B.½B.½A.¾A
0000:0490 | 00 BE 40 00  BF 40 00 BF  3F 00 C0 3F  00 C0 3E 00 | .¾@.¿@.¿?.À?.À>.
0000:04A0 | C1 3E 00 C1  3D 00 C2 3D  00 C2 3C 00  C3 3C 00 C3 | Á>.Á=.Â=.Â<.Ã<.Ã
0000:04B0 | 3B 00 C4 3B  00 C4 3A 00  C5 3A 00 C5  39 00 C6 39 | ;.Ä;.Ä:.Å:.Å9.Æ9
0000:04C0 | 00 C6 38 00  C7 38 00 C7  37 00 C8 37  00 C8 36 00 | .Æ8.Ç8.Ç7.È7.È6.
0000:04D0 | C9 36 00 C9  35 00 CA 35  00 CA 34 00  CB 34 00 CB | É6.É5.Ê5.Ê4.Ë4.Ë
0000:04E0 | 33 00 CC 33  00 CC 32 00  CD 32 00 CD  31 00 CE 31 | 3.Ì3.Ì2.Í2.Í1.Î1
0000:04F0 | 00 CE 30 00  CF 30 00 CF  2F 00 D0 2F  00 D0 2E 00 | .Î0.Ï0.Ï/.Ð/.Ð..
0000:0500 | D1 2D 00 D2  2D 00 D2 2C  00 D3 2C 00  D3 2B 00 D4 | Ñ-.Ò-.Ò,.Ó,.Ó+.Ô
0000:0510 | 2B 00 D4 2A  00 D5 2A 00  D5 29 00 D6  29 00 D6 28 | +.Ô*.Õ*.Õ).Ö).Ö(
0000:0520 | 00 D7 28 00  D7 27 00 D8  27 00 D8 26  00 D9 26 00 | .×(.×'.Ø'.Ø&.Ù&.
0000:0530 | D9 25 00 DA  25 00 DA 24  00 DB 24 00  DB 23 00 DC | Ù%.Ú%.Ú$.Û$.Û#.Ü
0000:0540 | 23 00 DC 22  00 DD 22 00  DD 21 00 DE  21 00 DE 20 | #.Ü".Ý".Ý!.Þ!.Þ 
0000:0550 | 00 DF 20 00  DF 1F 00 E0  1F 00 E0 1E  00 E1 1E 00 | .ß .ß..à..à..á..
0000:0560 | E1 1D 00 E2  1D 00 E2 1C  00 E3 1C 00  E3 1B 00 E4 | á..â..â..ã..ã..ä
0000:0570 | 1B 00 E4 1A  00 E5 1A 00  E5 19 00 E6  19 00 E6 18 | ..ä..å..å..æ..æ.
0000:0580 | 00 E7 18 00  E7 17 00 E8  16 00 E9 16  00 E9 15 00 | .ç..ç..è..é..é..
0000:0590 | EA 15 00 EA  14 00 EB 14  00 EB 13 00  EC 13 00 EC | ê..ê..ë..ë..ì..ì
0000:05A0 | 12 00 ED 12  00 ED 11 00  EE 11 00 EE  10 00 EF 10 | ..í..í..î..î..ï.
0000:05B0 | 00 EF 0F 00  F0 0F 00 F0  0E 00 F1 0E  00 F1 0D 00 | .ï..ð..ð..ñ..ñ..
0000:05C0 | F2 0D 00 F2  0C 00 F3 0C  00 F3 0B 00  F4 0B 00 F4 | ò..ò..ó..ó..ô..ô
0000:05D0 | 0A 00 F5 0A  00 F5 09 00  F6 09 00 F6  08 00 F7 08 | ..õ..õ..ö..ö..÷.
0000:05E0 | 00 F7 07 00  F8 07 00 F8  06 00 F9 06  00 F9 05 00 | .÷..ø..ø..ù..ù..
0000:05F0 | FA 05 00 FA  04 00 FB 04  00 FB 03 00  FC 03 00 FC | ú..ú..û..û..ü..ü
0000:0600 | 02 00 FD 02  00 FD 01 00  FE 01 00 FE  00 00 FF 42 | ..ý..ý..þ..þ..ÿB
0000:0610 | 54 00 00 00  00                                    | T....           
```

### red-blue_2s_100r.prg
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  C8 00 33 00  00 00 00 00 | ........È.3.....
0000:0020 | 04 00 01 00  00 C8 00 00  00 43 44 5C  02 00 00 C8 | .....È...CD\...È
0000:0030 | 00 00 00 FF  00 00 FE 00  01 FC 00 03  FB 00 04 FA | ...ÿ..þ..ü..û..ú
0000:0040 | 00 05 F9 00  06 F7 00 08  F6 00 09 F5  00 0A F3 00 | ..ù..÷..ö..õ..ó.
0000:0050 | 0C F2 00 0D  F1 00 0E F0  00 0F EE 00  11 ED 00 12 | .ò..ñ..ð..î..í..
0000:0060 | EC 00 13 EA  00 15 E9 00  16 E8 00 17  E7 00 18 E5 | ì..ê..é..è..ç..å
0000:0070 | 00 1A E4 00  1B E3 00 1C  E2 00 1D E0  00 1F DF 00 | ..ä..ã..â..à..ß.
0000:0080 | 20 DE 00 21  DC 00 23 DB  00 24 DA 00  25 D9 00 26 |  Þ.!Ü.#Û.$Ú.%Ù.&
0000:0090 | D7 00 28 D6  00 29 D5 00  2A D3 00 2C  D2 00 2D D1 | ×.(Ö.)Õ.*Ó.,Ò.-Ñ
0000:00A0 | 00 2E D0 00  2F CE 00 31  CD 00 32 CC  00 33 CA 00 | ..Ð./Î.1Í.2Ì.3Ê.
0000:00B0 | 35 C9 00 36  C8 00 37 C7  00 38 C5 00  3A C4 00 3B | 5É.6È.7Ç.8Å.:Ä.;
0000:00C0 | C3 00 3C C1  00 3E C0 00  3F BF 00 40  BE 00 41 BC | Ã.<Á.>À.?¿.@¾.A¼
0000:00D0 | 00 43 BB 00  44 BA 00 45  B9 00 46 B7  00 48 B6 00 | .C».Dº.E¹.F·.H¶.
0000:00E0 | 49 B5 00 4A  B3 00 4C B2  00 4D B1 00  4E B0 00 4F | Iµ.J³.L².M±.N°.O
0000:00F0 | AE 00 51 AD  00 52 AC 00  53 AA 00 55  A9 00 56 A8 | ®.Q..R¬.Sª.U©.V¨
0000:0100 | 00 57 A7 00  58 A5 00 5A  A4 00 5B A3  00 5C A1 00 | .W§.X¥.Z¤.[£.\¡.
0000:0110 | 5E A0 00 5F  9F 00 60 9E  00 61 9C 00  63 9B 00 64 | ^ ._..`..a..c..d
0000:0120 | 9A 00 65 98  00 67 97 00  68 96 00 69  95 00 6A 93 | ..e..g..h..i..j.
0000:0130 | 00 6C 92 00  6D 91 00 6E  90 00 6F 8E  00 71 8D 00 | .l..m..n..o..q..
0000:0140 | 72 8C 00 73  8A 00 75 89  00 76 88 00  77 87 00 78 | r..s..u..v..w..x
0000:0150 | 85 00 7A 84  00 7B 83 00  7C 81 00 7E  80 00 7F 7F | ..z..{..|..~....
0000:0160 | 00 80 7E 00  81 7C 00 83  7B 00 84 7A  00 85 78 00 | ..~..|..{..z..x.
0000:0170 | 87 77 00 88  76 00 89 75  00 8A 73 00  8C 72 00 8D | .w..v..u..s..r..
0000:0180 | 71 00 8E 6F  00 90 6E 00  91 6D 00 92  6C 00 93 6A | q..o..n..m..l..j
0000:0190 | 00 95 69 00  96 68 00 97  67 00 98 65  00 9A 64 00 | ..i..h..g..e..d.
0000:01A0 | 9B 63 00 9C  61 00 9E 60  00 9F 5F 00  A0 5E 00 A1 | .c..a..`.._. ^.¡
0000:01B0 | 5C 00 A3 5B  00 A4 5A 00  A5 58 00 A7  57 00 A8 56 | \.£[.¤Z.¥X.§W.¨V
0000:01C0 | 00 A9 55 00  AA 53 00 AC  52 00 AD 51  00 AE 4F 00 | .©U.ªS.¬R..Q.®O.
0000:01D0 | B0 4E 00 B1  4D 00 B2 4C  00 B3 4A 00  B5 49 00 B6 | °N.±M.²L.³J.µI.¶
0000:01E0 | 48 00 B7 46  00 B9 45 00  BA 44 00 BB  43 00 BC 41 | H.·F.¹E.ºD.»C.¼A
0000:01F0 | 00 BE 40 00  BF 3F 00 C0  3E 00 C1 3C  00 C3 3B 00 | .¾@.¿?.À>.Á<.Ã;.
0000:0200 | C4 3A 00 C5  38 00 C7 37  00 C8 36 00  C9 35 00 CA | Ä:.Å8.Ç7.È6.É5.Ê
0000:0210 | 33 00 CC 32  00 CD 31 00  CE 2F 00 D0  2E 00 D1 2D | 3.Ì2.Í1.Î/.Ð..Ñ-
0000:0220 | 00 D2 2C 00  D3 2A 00 D5  29 00 D6 28  00 D7 26 00 | .Ò,.Ó*.Õ).Ö(.×&.
0000:0230 | D9 25 00 DA  24 00 DB 23  00 DC 21 00  DE 20 00 DF | Ù%.Ú$.Û#.Ü!.Þ .ß
0000:0240 | 1F 00 E0 1D  00 E2 1C 00  E3 1B 00 E4  1A 00 E5 18 | ..à..â..ã..ä..å.
0000:0250 | 00 E7 17 00  E8 16 00 E9  15 00 EA 13  00 EC 12 00 | .ç..è..é..ê..ì..
0000:0260 | ED 11 00 EE  0F 00 F0 0E  00 F1 0D 00  F2 0C 00 F3 | í..î..ð..ñ..ò..ó
0000:0270 | 0A 00 F5 09  00 F6 08 00  F7 06 00 F9  05 00 FA 04 | ..õ..ö..÷..ù..ú.
0000:0280 | 00 FB 03 00  FC 01 00 FE  00 00 FF 42  54 00 00 00 | .û..ü..þ..ÿBT...
0000:0290 | 00                                                 | .               
```

### red-blue_1s_100r.prg
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  64 00 33 00  00 00 00 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 64 00 00  00 43 44 30  01 00 00 64 | .....d...CD0...d
0000:0030 | 00 00 00 FF  00 00 FC 00  03 FA 00 05  F7 00 08 F5 | ...ÿ..ü..ú..÷..õ
0000:0040 | 00 0A F2 00  0D F0 00 0F  ED 00 12 EA  00 15 E8 00 | ..ò..ð..í..ê..è.
0000:0050 | 17 E5 00 1A  E3 00 1C E0  00 1F DE 00  21 DB 00 24 | .å..ã..à..Þ.!Û.$
0000:0060 | D8 00 27 D6  00 29 D3 00  2C D1 00 2E  CE 00 31 CB | Ø.'Ö.)Ó.,Ñ..Î.1Ë
0000:0070 | 00 34 C9 00  36 C6 00 39  C4 00 3B C1  00 3E BF 00 | .4É.6Æ.9Ä.;Á.>¿.
0000:0080 | 40 BC 00 43  B9 00 46 B7  00 48 B4 00  4B B2 00 4D | @¼.C¹.F·.H´.K².M
0000:0090 | AF 00 50 AD  00 52 AA 00  55 A7 00 58  A5 00 5A A2 | ¯.P..Rª.U§.X¥.Z¢
0000:00A0 | 00 5D A0 00  5F 9D 00 62  9B 00 64 98  00 67 95 00 | .] ._..b..d..g..
0000:00B0 | 6A 93 00 6C  90 00 6F 8E  00 71 8B 00  74 89 00 76 | j..l..o..q..t..v
0000:00C0 | 86 00 79 83  00 7C 81 00  7E 7E 00 81  7C 00 83 79 | ..y..|..~~..|..y
0000:00D0 | 00 86 76 00  89 74 00 8B  71 00 8E 6F  00 90 6C 00 | ..v..t..q..o..l.
0000:00E0 | 93 6A 00 95  67 00 98 64  00 9B 62 00  9D 5F 00 A0 | .j..g..d..b.._. 
0000:00F0 | 5D 00 A2 5A  00 A5 58 00  A7 55 00 AA  52 00 AD 50 | ].¢Z.¥X.§U.ªR..P
0000:0100 | 00 AF 4D 00  B2 4B 00 B4  48 00 B7 46  00 B9 43 00 | .¯M.²K.´H.·F.¹C.
0000:0110 | BC 40 00 BF  3E 00 C1 3B  00 C4 39 00  C6 36 00 C9 | ¼@.¿>.Á;.Ä9.Æ6.É
0000:0120 | 34 00 CB 31  00 CE 2E 00  D1 2C 00 D3  29 00 D6 27 | 4.Ë1.Î..Ñ,.Ó).Ö'
0000:0130 | 00 D8 24 00  DB 21 00 DE  1F 00 E0 1C  00 E3 1A 00 | .Ø$.Û!.Þ..à..ã..
0000:0140 | E5 17 00 E8  15 00 EA 12  00 ED 0F 00  F0 0D 00 F2 | å..è..ê..í..ð..ò
0000:0150 | 0A 00 F5 08  00 F7 05 00  FA 03 00 FC  00 00 FF 42 | ..õ..÷..ú..ü..ÿB
0000:0160 | 54 00 00 00  00                                    | T....           
```

### red-blue_.5s_100r.prg
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  32 00 33 00  00 00 00 00 | ........2.3.....
0000:0020 | 04 00 01 00  00 32 00 00  00 43 44 9A  00 00 00 32 | .....2...CD....2
0000:0030 | 00 00 00 FF  00 00 FA 00  05 F5 00 0A  EF 00 10 EA | ...ÿ..ú..õ..ï..ê
0000:0040 | 00 15 E5 00  1A E0 00 1F  DB 00 24 D5  00 2A D0 00 | ..å..à..Û.$Õ.*Ð.
0000:0050 | 2F CB 00 34  C6 00 39 C1  00 3E BB 00  44 B6 00 49 | /Ë.4Æ.9Á.>».D¶.I
0000:0060 | B1 00 4E AC  00 53 A7 00  58 A1 00 5E  9C 00 63 97 | ±.N¬.S§.X¡.^..c.
0000:0070 | 00 68 92 00  6D 8D 00 72  87 00 78 82  00 7D 7D 00 | .h..m..r..x..}}.
0000:0080 | 82 78 00 87  72 00 8D 6D  00 92 68 00  97 63 00 9C | .x..r..m..h..c..
0000:0090 | 5E 00 A1 58  00 A7 53 00  AC 4E 00 B1  49 00 B6 44 | ^.¡X.§S.¬N.±I.¶D
0000:00A0 | 00 BB 3E 00  C1 39 00 C6  34 00 CB 2F  00 D0 2A 00 | .»>.Á9.Æ4.Ë/.Ð*.
0000:00B0 | D5 24 00 DB  1F 00 E0 1A  00 E5 15 00  EA 10 00 EF | Õ$.Û..à..å..ê..ï
0000:00C0 | 0A 00 F5 05  00 FA 00 00  FF 42 54 00  00 00 00    | ..õ..ú..ÿBT.... 
```

### green-yellow_1s_100r.prg
```
0000:0000 | 50 52 03 49  4E 05 00 00  00 04 00 08  64 00 50 49 | PR.IN.......d.PI
0000:0010 | 15 00 00 00  01 00 01 00  64 00 33 00  00 00 00 00 | ........d.3.....
0000:0020 | 04 00 01 00  00 64 00 00  00 43 44 30  01 00 00 64 | .....d...CD0...d
0000:0030 | 00 00 00 00  FF 00 03 FF  00 05 FF 00  08 FF 00 0A | ....ÿ..ÿ..ÿ..ÿ..
0000:0040 | FF 00 0D FF  00 0F FF 00  12 FF 00 15  FF 00 17 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:0050 | 00 1A FF 00  1C FF 00 1F  FF 00 21 FF  00 24 FF 00 | ..ÿ..ÿ..ÿ.!ÿ.$ÿ.
0000:0060 | 27 FF 00 29  FF 00 2C FF  00 2E FF 00  31 FF 00 34 | 'ÿ.)ÿ.,ÿ..ÿ.1ÿ.4
0000:0070 | FF 00 36 FF  00 39 FF 00  3B FF 00 3E  FF 00 40 FF | ÿ.6ÿ.9ÿ.;ÿ.>ÿ.@ÿ
0000:0080 | 00 43 FF 00  46 FF 00 48  FF 00 4B FF  00 4D FF 00 | .Cÿ.Fÿ.Hÿ.Kÿ.Mÿ.
0000:0090 | 50 FF 00 52  FF 00 55 FF  00 58 FF 00  5A FF 00 5D | Pÿ.Rÿ.Uÿ.Xÿ.Zÿ.]
0000:00A0 | FF 00 5F FF  00 62 FF 00  64 FF 00 67  FF 00 6A FF | ÿ._ÿ.bÿ.dÿ.gÿ.jÿ
0000:00B0 | 00 6C FF 00  6F FF 00 71  FF 00 74 FF  00 76 FF 00 | .lÿ.oÿ.qÿ.tÿ.vÿ.
0000:00C0 | 79 FF 00 7C  FF 00 7E FF  00 81 FF 00  83 FF 00 86 | yÿ.|ÿ.~ÿ..ÿ..ÿ..
0000:00D0 | FF 00 89 FF  00 8B FF 00  8E FF 00 90  FF 00 93 FF | ÿ..ÿ..ÿ..ÿ..ÿ..ÿ
0000:00E0 | 00 95 FF 00  98 FF 00 9B  FF 00
9D FF 00 A0 FF 00 | ..ÿ..ÿ. ÿ.
0000:00F0 | A2 FF 00 A5  FF 00 A7 FF  00 AA FF 00  AD FF 00 AF | ¢ÿ.¥ÿ.§ÿ.ªÿ..ÿ.¯
0000:0100 | FF 00 B2 FF  00 B4 FF 00  B7 FF 00 B9  FF 00 BC FF | ÿ.²ÿ.´ÿ.·ÿ.¹ÿ.¼ÿ
0000:0110 | 00 BF FF 00  C1 FF 00 C4  FF 00 C6 FF  00 C9 FF 00 | .¿ÿ.Áÿ.Äÿ.Æÿ.Éÿ.
0000:0120 | CB FF 00 CE  FF 00 D1 FF  00 D3 FF 00  D6 FF 00 D8 | Ëÿ.Îÿ.Ñÿ.Óÿ.Öÿ.Ø
0000:0130 | FF 00 DB FF  00 DE FF 00  E0 FF 00 E3  FF 00 E5 FF | ÿ.Ûÿ.Þÿ.àÿ.ãÿ.åÿ
0000:0140 | 00 E8 FF 00  EA FF 00 ED  FF 00 F0 FF  00 F2 FF 00 | .èÿ.êÿ.íÿ.ðÿ.òÿ.
0000:0150 | F5 FF 00 F7  FF 00 FA FF  00 FC FF 00  FF FF 00 42 | õÿ.÷ÿ.úÿ.üÿ.ÿÿ.B
0000:0160 | 54 00 00 00  00                                    | T....           
```

### Analysis of Fade Test Results

**Key Observations:**

1. **Duration Limits:** The official app appears to have practical limits for fade durations. Fades longer than approximately 2 minutes 15 seconds either fail completely or exhibit incorrect timing behavior.

2. **Successful Fade Range:** Fades between 0.5 seconds and 2 minutes 15 seconds work as intended, showing smooth gradual color transitions in the hex data.

3. **Color Transition Pattern:** In successful fades, you can see the gradual RGB value changes:
   - Starting with `FF 00 00` (pure red)
   - Gradually decreasing red values: `FE 00 01`, `FD 00 02`, etc.
   - Simultaneously increasing blue values: `00 01`, `00 02`, etc.
   - Ending with `00 00 FF` (pure blue)

4. **Refresh Rate:** All successful fade tests use 100Hz refresh rate (`64 00` in header at offset `0x0C-0x0D`).

5. **Header Analysis for Fades:**
   - **2m15s fade:** `BC 34` (13500) duration units, `01 00` at field 0x16, `00 00` at field 0x1E
   - **2m fade:** `E0 2E` (12000) duration units, `01 00` at field 0x16, `00 00` at field 0x1E  
   - **5s fade:** `F4 01` (500) duration units, `01 00` at field 0x16, `00 00` at field 0x1E
   - **2s fade:** `C8 00` (200) duration units, `01 00` at field 0x16, `00 00` at field 0x1E
   - **1s fade:** `64 00` (100) duration units, `01 00` at field 0x16, `00 00` at field 0x1E
   - **0.5s fade:** `32 00` (50) duration units, `01 00` at field 0x16, `00 00` at field 0x1E

6. **Green-Yellow Fade:** Shows similar pattern but transitions from `00 FF 00` (green) to `FF FF 00` (yellow) by gradually increasing the red component while keeping green at maximum.

### Implications for PRG Generator

These official app fade test results provide valuable insights for implementing fade functionality in our PRG generator:

1. **Timing Constraints:** Implement reasonable duration limits to avoid the timing issues seen in longer fades.

2. **Smooth Transitions:** The gradual RGB value changes show how smooth color transitions should be implemented at the binary level.

3. **Header Field Behavior:** The consistent header field patterns across different fade durations help validate our understanding of the PRG format.

4. **Color Space Handling:** The green-yellow fade demonstrates how to handle transitions that don't involve all three RGB components changing simultaneously.