
* Define sets
Set H  hot process streams
         /
1*17
         / ;

Set C  cold process streams
         /
1*17
         / ;

* Input parameters
Parameter FCpH0(H)  F*Cp for hot process streams
         /
1        6
2        2
3        0.5
4        8
5        3
6        4
7        0.2
8        0.6
9        1.5
10        4
11        12
12        8
13        5
14        0.6
15        0.3
16        6
17        0.9
         / ;

Parameter FCpC0(C)  F*Cp for cold process streams
         /
1        14
2        3
3        0.4
4        2.5
5        2
6        6
7        1.5
8        0.2
9        5.5
10        3
11        8
12        12
13        0.3
14        4.5
15        1
16        0.1
17        7
         / ;

Parameter FCpH(H)  F*Cp for hot process streams ;
Parameter FCpC(C)  F*Cp for cold process streams ;

execseed = 1 + gmillisec(jnow);

Loop(H,
     If(FCpH0(H) < 1,
        FCpH(H) = uniformint(ceil(0.9*10*FCpH0(H)), floor(1.1*10*FCpH0(H)))/10;
       );
     If(FCpH0(H) >= 1 and FCpH0(H) < 6,
        FCpH(H) = uniformint(ceil(0.9*2*FCpH0(H)), floor(1.1*2*FCpH0(H)))/2;
       );
     If(FCpH0(H) >= 6,
        FCpH(H) = uniformint(ceil(0.9*FCpH0(H)), floor(1.1*FCpH0(H)));
       );
    );

Loop(C,
     If(FCpC0(C) < 1,
        FCpC(C) = uniformint(ceil(0.9*10*FCpC0(C)), floor(1.1*10*FCpC0(C)))/10;
       );
     If(FCpC0(C) >= 1 and FCpC0(C) < 6,
        FCpC(C) = uniformint(ceil(0.9*2*FCpC0(C)), floor(1.1*2*FCpC0(C)))/2;
       );
     If(FCpC0(C) >= 6,
        FCpC(C) = uniformint(ceil(0.9*FCpC0(C)), floor(1.1*FCpC0(C)));
       );
    );

display FCpH, FCpC;

file fout  / Transshipment_Iutput_Unbalanced_17H_17C.inc /;
put fout;
put "Set H  hot process streams"/;
put "/"/;
put "1*17"/;
put "/ ;"//;
put "Set C  cold process streams"/;
put "/"/;
put "1*17"/;
put "/ ;"//;
put "Parameter FCpH(H)  F*Cp for hot process streams"/;
put "/"/;
Loop(H,
     put H.tl, @6, FCpH(H)/;
    );
put "/ ;"//;
put "Parameter FCpC(C)  F*Cp for cold process streams"/;
put "/"/;
Loop(C,
     put C.tl, @6, FCpC(C)/;
    );
put "/ ;"//;
putclose;

