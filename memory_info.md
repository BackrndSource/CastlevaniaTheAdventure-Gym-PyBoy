# Castlevania: The Adventure (GB)

## Score

0xC034      BCD (Byte lenght 3: 0xC034-0xC036)

## Time left

0xC436      Seconds BCD
0xC437      Minutes BCD

## Lives left

0xC040    Vidas restantes

## Health

0xC519    Salud restante (00-0A) (0-10)

## Whipe

0xC51C      Whipe level

            00  Normal
            01  Medium
            02  High (Throw bullet)
            

0xC51D      Whipe can throw bullet

            00  Deny
            80  Allow

            If 0xC51C (Whipe level) is 02 and 0xC51E > 01 (game sets 80) then whipe throw bullet

## Scenario

0xC006      Escenario en que te encuentras?

            00  Brand
            01  Start menu
            02  ??
            03  Start pressed
            04  Stats menu
            05  Playable level 1

## Invincible

0xC02C      Timer

            00  Normal
            FF  Maximo tiempo de invencibilidad (35s aprox)

## Position

0xC50B      X axis
0xC50C      X axis^2

0xC42B      X axis
0xC42C      X axis*256


0xC512      Y axis (16 is top, change when crouched or jumping)
0xC300      Y axis (0 is top, change when crouched or jumping)

0xC412      Room

0xC511      Distance from floor (0 is grounded, quickly scalates)

## Character state 

0xC502      O Normal
            1 In air (also activated when jumping or receive damage)
            2 crouched
            3 in rope
            4 atacking