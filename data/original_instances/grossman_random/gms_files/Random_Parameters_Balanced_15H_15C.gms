
* Define sets
Set H  hot process streams
         /
1*15
         / ;

Set C  cold process streams
         /
1*15
         / ;

* Input parameters
Parameter FCpH0(H)  F*Cp for hot process streams
         /
1        1
2        2
3        1.5
4        2.5
5        1.7
6        0.8
7        1.2
8        1.8
9        1.1
10        1.3
11        2.1
12        2.2
13        1.2
14        1.6
15        1.9
         / ;

Parameter FCpC0(C)  F*Cp for cold process streams
         /
1        1.5
2        1.3
3        2.5
4        2.8
5        1.9
6        0.8
7        1.7
8        1.6
9        0.9
10        2.1
11        1.8
12        1.2
13        1.6
14        1.4
15        2
         / ;

Parameter FCpH(H)  F*Cp for hot process streams ;
Parameter FCpC(C)  F*Cp for cold process streams ;

execseed = 1 + gmillisec(jnow);

FCpH(H) = uniformint(ceil(0.9*10*FCpH0(H)), floor(1.1*10*FCpH0(H)))/10;
FCpC(C) = uniformint(ceil(0.9*10*FCpC0(C)), floor(1.1*10*FCpC0(C)))/10;

display FCpH, FCpC;

file fout  / Transshipment_Iutput_Balanced_15H_15C.inc /;
put fout;
put "Set H  hot process streams"/;
put "/"/;
put "1*15"/;
put "/ ;"//;
put "Set C  cold process streams"/;
put "/"/;
put "1*15"/;
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
