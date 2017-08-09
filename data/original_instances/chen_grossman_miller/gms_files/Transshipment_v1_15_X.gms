
******************************************************************
******************************************************************
*
* DOWNLOADED FROM MINLP CYBER-INFRASTRUCTURE 
* www.minlp.org
*
* PROBLEM : Large-Scale MILP Transshipment Models for Heat Exchanger Network Synthesis
*
* AUTHOR(S) : Yang Chen, Ignacio Grossmann, David Miller
*
* SUBMITTED BY : Yang Chen

******************************************************************
******************************************************************* LP and MILP Transshipment model for heat integration
* by Yang Chen, start on 2012-12-18, last modified on 2013-2-8

* Setup output format
* listing of the input file on or off
* $offlisting
* cross reference map on or off
* $offsymxref
* symbol list on or off
* $offsymlist
* number of equations listed per block in list file
* Option limrow = 100;
* number of variables listed per block in list file
* Option limcol = 100;
* solver status on or off
* Option sysout = off;
* solution report on or off
* Option solprint = off;

* Define sets
Set H  hot process streams
         /
1*15
         / ;

Set C  cold process streams
         /
1*15
         / ;

Set S  hot utility streams
         / 1*2 / ;

Set W  cold utility streams
         / 1*1 / ;

Set K  possible temperature intervals
         / 1*100 / ;

* Input parameters
Parameter FCpH(H)  F*Cp for hot process streams
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
         / ;

Parameter FCpC(C)  F*Cp for cold process streams
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
         / ;

Parameter TinH(H)  inlet temperature of hot process streams
         /
1        400
2        340
3        380
4        300
5        420
6        390
7        360
8        280
9        250
10        330
11        430
12        200
13        150
14        330
15        370
         / ;

Parameter ToutH(H)  outlet temperature of hot process streams
         /
1        120
2        120
3        150
4        100
5        160
6        110
7        200
8        130
9        80
10        170
11        300
12        100
13        70
14        180
15        115
         / ;

Parameter TinC(C)  inlet temperature of cold process streams
         /
1        160
2        100
3        50
4        200
5        150
6        100
7        200
8        120
9        110
10        190
11        260
12        80
13        130
14        180
15        155
         / ;

Parameter ToutC(C)  outlet temperature of cold process streams
         /
1        400
2        250
3        300
4        380
5        450
6        180
7        350
8        330
9        220
10        360
11        420
12        180
13        390
14        260
15        365
         / ;

Parameter TinS(S)  inlet temperature of hot utility streams
         / 1   500
           2   350 / ;

Parameter ToutS(S)  outlet temperature of hot utility streams
         / 1   499
           2   349 / ;

Parameter TinW(W)  inlet temperature of cold utility streams
         / 1   20 / ;

Parameter ToutW(W)  outlet temperature of cold utility streams
         / 1   21 / ;

Parameter WW(W)  whether the cold utility is cooling water
         / 1   1 /;

Parameter ToutWA(W)  actual outlet temperature of cold utility
         / 1   50 / ;

Parameter CS(S)  cost of hot utilities
         / 1   80
           2   50 / ;

Parameter CW(W)  cost of cold utilities
         / 1   20 / ;

* Define temperature intervals
Scalar dT  minimum recovery approach temperature
         / 10 / ;

Alias (K, K2);

Alias (H, H2);
Alias (C, C2);
Alias (S, S2);
Alias (W, W2);

Parameters
    TH(K)  hot side end points of temperature intervals
    TC(K)  cold side end points of temperature intervals
    NKT  actual number of end points of temperature intervals
    NK  actual number of temperature intervals ;

TH(K) = 0;
TC(K) = 0;

Parameter Tmax  the maximum temperature of process streams ;
Parameter Tmin  the minimum temperature of process streams ;

Scalar temp  a temporary parameter  / 0 / ;
Scalar temp2  a temporary parameter  / 0 / ;
Scalar temp3  a temporary parameter  / 0 / ;
Scalar temp4  a temporary parameter  / 0 / ;
scalar ind  a indicator  / 1 /;
scalar ind2  a indicator  / 1 /;

Tmax = max( smax(H, TinH(H)), smax(C, ToutC(C) + dT) );
Tmin = min( smin(H, ToutH(H)), smin(C, TinC(C) + dT) );

TH(K)$(ord(K) = 1) = Tmax;

temp2 = Tmax;

Loop(K $ (ord(K) > 1 and ind = 1),
     temp = 0;
     ind = 0;
     Loop(H $ (TinH(H) < Tmax and TinH(H) > Tmin and TinH(H) > temp and TinH(H) < temp2),
          temp = TinH(H);
          ind = 1;
         );
     Loop(C $ (TinC(C)+dT < Tmax and TinC(C)+dT > Tmin and TinC(C)+dT > temp and TinC(C)+dT < temp2),
          temp = TinC(C) + dT;
          ind = 1;
         );
     Loop(S $ (TinS(S) < Tmax and TinS(S) > Tmin and TinS(S) > temp and TinS(S) < temp2),
          temp = TinS(S);
          ind = 1;
         );
     Loop(W $ (TinW(W)+dT < Tmax and TinW(W)+dT > Tmin and TinW(W)+dT > temp and TinW(W)+dT < temp2),
          temp = TinW(W) + dT;
          ind = 1;
         );
     TH(K) = temp;
     temp2 = temp;
     NKT = ord(K);
    );

TH(K)$(ord(K) = NKT) = Tmin;

TC(K) = TH(K) - dT $ (ord(K) <= NKT);

NK = NKT - 1;

* Determine whether some process stream in within some temperature interval
Parameters
    Hk(H,K)  hot process stream within temperature interval
    Hkp(H,K)  hot process stream within and above temperature interval
    Ck(C,K)  cold process stream within temperature interval
    Sk(S,K)  hot utility stream within temperature interval
    Skp(S,K)  hot utility stream within and above temperature interval
    Wk(W,K)  cold utility stream within temperature interval ;

Hk(H,K) = 0;
Hkp(H,K) = 0;
Ck(C,K) = 0;
Sk(S,K) = 0;
Skp(S,K) = 0;
Wk(W,K) = 0;

Loop(K $ (ord(K) <= NK),
     Hk(H,K) = 1 $ (TinH(H) >= TH(K) and ToutH(H) < TH(K));
     Hkp(H,K) = 1 $ (TinH(H) >= TH(K));
     Ck(C,K) = 1 $ (TinC(C) <= TC(K+1) and ToutC(C) > TC(K+1));
     Sk(S,K) = 1 $ ((TinS(S) >= TH(K) and ToutS(S) < TH(K))
                    or (TinS(S) > TH(K) and ord(K) = 1));
     Skp(S,K) = 1 $ (TinS(S) >= TH(K));
     Wk(W,K) = 1 $ ((TinW(W) <= TC(K+1) and ToutW(W) > TC(K+1))
                    or (TinW(W) < TC(K+1) and ord(K) = NK));
    );

Scalar indK  indicator for temperature intervals for utilities  / 1 / ;
Loop(S,
     If(sum(K$(ord(K) <= NK), Sk(S,K)) > 1,
        indK = 1;
        Loop(K $ (Sk(S,K) = 1 and ord(K) <= NK),
             If(indK = 0,
                Sk(S,K) = 0;
               );
             If(Sk(S,K) = 1,
                indK = 0;
               );
            );
       );
    );
Loop(W,
     If(sum(K$(ord(K) <= NK), Wk(W,K)) > 1,
        indK = 1;
        Loop(K $ (ord(K) <= NK),
             Loop(K2 $ (ord(K2) = NK + 1 - ord(K) and Wk(W,K2) = 1),
                  If(indK = 0,
                     Wk(W,K2) = 0;
                    );
                  If(Wk(W,K2) = 1,
                     indK = 0;
                    );
                 );
            );
       );
    );

* Determine heat contents of process streams and utilities
Parameters
    QH(H,K)  heat contents of hot process streams
    QC(C,K)  heat contents of cold process streams ;

QH(H,K) = 0;
QC(C,K) = 0;

QH(H,K) = FCpH(H)*(TH(K) - max(TH(K+1), ToutH(H))) $ (Hk(H,K) = 1);
QC(C,K) = FCpC(C)*(min(TC(K), ToutC(C)) - TC(K+1)) $ (Ck(C,K) = 1);

Parameters
    QHT(H)  total heat contents of hot process streams
    QCT(C)  total heat contents of cold process streams ;

QHT(H) = FCpH(H)*(TinH(H) - ToutH(H));
QCT(C) = FCpC(C)*(ToutC(C) - TinC(C));

* Define upper and lower bounds for exchanged heat load
Parameters
    QHCLO(H,C,K)  lower boounds of heat exchange between hot streams and cold streams at intervals
    QSCLO(S,C,K)  lower boounds of heat exchange between hot utilities and cold streams at intervals
    QHWLO(H,W,K)  lower boounds of heat exchange between hot streams and cold utilities at intervals
    QHCUP(H,C,K)  upper boounds of heat exchange between hot streams and cold streams at intervals
    QSCUP(S,C,K)  upper boounds of heat exchange between hot utilities and cold streams at intervals
    QHWUP(H,W,K)  upper boounds of heat exchange between hot streams and cold utilities at intervals ;

    QHCLO(H,C,K) = 0;
    QSCLO(S,C,K) = 0;
    QHWLO(H,W,K) = 0;
    QHCUP(H,C,K) = +inf;
    QSCUP(S,C,K) = +inf;
    QHWUP(H,W,K) = +inf;

* Define heat residuals
Parameter
    R(K)  total heat residual exiting temperature intervals ;

    R(K) = 0;


* Parameters determining whether the cost of cooling water needs to be re-calculated
Parameter FCpHT(K)  F*Cp for total hot process streams;
Parameter QHTK(K)  total heat contents of hot process streams in temperature intervals;
Parameter QHWT(W,K)  total heat exchange between hot streams and cold utilities;
Parameter FHWT(W,K)  fraction of heat exchange between hot streams and cold utilities;
Parameter FCost(W)  fraction of cooling water cost;

FCpHT(K) = sum(H$(Hk(H,K)=1), FCpH(H));
QHTK(K) = sum(H, QH(H,K));
QHWT(W,K) = 0;
FHWT(W,K) = 0;
FCost(W) = 1;

Set Sol  set for re-calculations  / 1*10 / ;
Scalar NSol  number of calculations  / 1 /;


* Define subnetworks and related parameters
Set N  possible subnetworks dividing by pinch points
         / 1*5 / ;

Scalar NN  number of subnetworks   / 1 / ;

Parameters
    KN(K,N)  existence of temperature intervals in subnetworks ;

KN(K,N) = 0;

Parameters
    TN(N)  end temperature interval for each subnetwork ;

TN(N) = 0;

Parameters
    Hkn(H,K)  hot process stream within temperature interval in subnetworks
    Skn(S,K)  hot process stream within temperature interval in subnetworks ;

Hkn(H,K) = 0;
Skn(S,K) = 0;

Parameters
    MHC(H,C,N)  existence of matches between hot streams and cold streams in subnetworks
    MSC(S,C,N)  existence of matches between hot utilities and cold streams in subnetworks
    MHW(H,W,N)  existence of matches between hot streams and cold utilities in subnetworks ;

MHC(H,C,N) = 0;
MSC(S,C,N) = 0;
MHW(H,W,N) = 0;

Parameters
    QHTN(H,N)  total heat contents of hot process streams in subnetworks
    QCTN(C,N)  total heat contents of cold process streams in subnetworks ;

QHTN(H,N) = 0;
QCTN(C,N) = 0;

Parameters
    UHCN(H,C,N)  upper bounds of exchanged heat between hot streams and cold streams
    USCN(S,C,N)  upper bounds of exchanged heat between hot utilities and cold streams
    UHWN(H,W,N)  upper bounds of exchanged heat between hot streams and cold utilities ;

UHCN(H,C,N) = +inf;
USCN(S,C,N) = +inf;
UHWN(H,W,N) = +inf;

Parameters
    MH(H,N)  existence of hot streams in subnetworks
    MC(C,N)  existence of cold streams in subnetworks
    MS(S,N)  existence of hot streams in subnetworks
    MW(W,N)  existence of cold utilities in subnetworks ;

MH(H,N) = 0;
MC(C,N) = 0;
MS(S,N) = 0;
MW(W,N) = 0;

Parameters
    NH(N)  existence of hot streams in subnetworks
    NC(N)  existence of cold streams in subnetworks
    NS(N)  existence of hot streams in subnetworks
    NW(N)  existence of cold utilities in subnetworks
    Nmin(N)  minimum number of heat exchangers in subnetworks ;

NH(N) = 0;
NC(N) = 0;
NS(N) = 0;
NW(N) = 0;
Nmin(N) = 0;

Parameters
    QHCN(H,C,N)  exchanged heat between hot streams and cold streams in subnetworks
    QSCN(S,C,N)  exchanged heat between hot streams and cold streams in subnetworks
    QHWN(H,W,N)  exchanged heat between hot streams and cold streams in subnetworks ;

QHCN(H,C,N) = 0;
QSCN(S,C,N) = 0;
QHWN(H,W,N) = 0;

Alias (N, N2);

Scalar
    N_index  index of set N   / 1 / ;

Scalar
    ZYT  total number of heat exchangers   / 0 / ;


Scalars
    Time_LP  solution time for LP model   / 0 /
    Time_MILP  solution time for MILP model   / 0 / ;


* Define variables
Positive Variables
    QS(S)  heat load of hot utilities
    QW(W)  heat load of cold utilities ;

Positive Variables
    QHC(H,C,K)  exchange of heat of hot streams and cold streams at intervals
    QSC(S,C,K)  exchange of heat of hot utilities and cold streams at intervals
    QHW(H,W,K)  exchange of heat of hot streams and cold utilities at intervals
    RH(H,K)  heat residual of hot streams exiting intervals
    RS(S,K)  heat residual of hot utilities exiting intervals ;

    RH.fx(H,K)$(ord(K)=NK) = 0;

    QHC.lo(H,C,K) = QHCLO(H,C,K);
    QHC.up(H,C,K) = QHCUP(H,C,K);
    QSC.lo(S,C,K) = QSCLO(S,C,K);
    QSC.up(S,C,K) = QSCUP(S,C,K);
    QHW.lo(H,W,K) = QHWLO(H,W,K);
    QHW.up(H,W,K) = QHWUP(H,W,K);

Binary Variables
    yHC(H,C,N)  matches between hot streams and cold streams in subnetworks
    ySC(S,C,N)  matches between hot utilities and cold streams in subnetworks
    yHW(H,W,N)  matches between hot streams and cold utilities in subnetworks ;

Variable
    Z  objective function for LP model ;

Variable
    ZY   objective function for MILP model ;


* Define equations
Equations
    Obj  objective function for LP model ;

    Obj..  Z =e= sum(S, CS(S)*QS(S)) + sum(W, CW(W)*QW(W));

Equations
    ObjYN  objective function for MILP model ;

    ObjYN..  ZY =e= sum((H,C,N)$(ord(N) = N_index and MHC(H,C,N) = 1), yHC(H,C,N))
                  + sum((S,C,N)$(ord(N) = N_index and MSC(S,C,N) = 1), ySC(S,C,N))
                  + sum((H,W,N)$(ord(N) = N_index and MHW(H,W,N) = 1), yHW(H,W,N));

Equations
    HeatBalH(H,K)  heat balance of hot streams at intervals
    HeatBalS(S,K)  heat balance of hot utilities at intervals
    HeatBalC(C,K)  heat balance of cold streams at intervals
    HeatBalW(W,K)  heat balance of cold utilities at intervals ;

    HeatBalH(H,K) $ (Hkp(H,K) = 1) ..
        RH(H,K) - RH(H,K-1)$(Hkp(H,K-1)=1) + sum(C$(Ck(C,K)=1), QHC(H,C,K))
            + sum(W$(Wk(W,K)=1), QHW(H,W,K)) =e= QH(H,K);

    HeatBalS(S,K) $ (Skp(S,K) = 1) ..
        RS(S,K) - RS(S,K-1)$(Skp(S,K-1)=1) + sum(C$(Ck(C,K)=1), QSC(S,C,K))
            - QS(S)$(Sk(S,K)=1) =e= 0;

    HeatBalC(C,K) $ (Ck(C,K) = 1) ..
        sum(H$(Hkp(H,K)=1), QHC(H,C,K)) + sum(S$(Skp(S,K)=1), QSC(S,C,K))
            =e= QC(C,K);

    HeatBalW(W,K) $ (Wk(W,K) = 1) ..
        sum(H$(Hkp(H,K)=1), QHW(H,W,K)) - QW(W) =e= 0;


Equations
    HeatBalHN(H,K,N)  heat balance of hot streams at intervals in subnetworks
    HeatBalSN(S,K,N)  heat balance of hot utilities at intervals in subnetworks
    HeatBalCN(C,K,N)  heat balance of cold streams at intervals in subnetworks
    HeatBalWN(W,K,N)  heat balance of cold utilities at intervals in subnetworks ;

    HeatBalHN(H,K,N) $ (ord(N) = N_index and KN(K,N) = 1 and Hkp(H,K) = 1) ..
        RH(H,K) - RH(H,K-1)$(Hkp(H,K-1)=1 and KN(K-1,N)=1) + sum(C$(Ck(C,K)=1), QHC(H,C,K))
            + sum(W$(Wk(W,K)=1), QHW(H,W,K)) =e= QH(H,K);

    HeatBalSN(S,K,N) $ (ord(N) = N_index and KN(K,N) = 1 and Skp(S,K) = 1) ..
        RS(S,K) - RS(S,K-1)$(Skp(S,K-1)=1 and KN(K-1,N)=1) + sum(C$(Ck(C,K)=1), QSC(S,C,K))
            - QS(S)$(Sk(S,K)=1) =e= 0;

    HeatBalCN(C,K,N) $ (ord(N) = N_index and KN(K,N) = 1 and Ck(C,K) = 1) ..
        sum(H$(Hkp(H,K)=1), QHC(H,C,K)) + sum(S$(Skp(S,K)=1), QSC(S,C,K))
            =e= QC(C,K);

    HeatBalWN(W,K,N) $ (ord(N) = N_index and KN(K,N) = 1 and Wk(W,K) = 1) ..
        sum(H$(Hkp(H,K)=1), QHW(H,W,K)) - QW(W) =e= 0;

Equations
    MatchHCN(H,C,N)  matches between hot streams and cold streams in subnetworks
    MatchSCN(S,C,N)  matches between hot utilities and cold streams in subnetworks
    MatchHWN(H,W,N)  matches between hot streams and cold utilities in subnetworks ;

    MatchHCN(H,C,N) $ (ord(N) = N_index and MHC(H,C,N) = 1) ..
        sum(K$(KN(K,N)=1 and Hkp(H,K)=1 and Ck(C,K) = 1), QHC(H,C,K)) - UHCN(H,C,N)*yHC(H,C,N) =l= 0;

    MatchSCN(S,C,N) $ (ord(N) = N_index and MSC(S,C,N) = 1) ..
        sum(K$(KN(K,N)=1 and Skp(S,K)=1 and Ck(C,K) = 1), QSC(S,C,K)) - USCN(S,C,N)*ySC(S,C,N) =l= 0;

    MatchHWN(H,W,N) $ (ord(N) = N_index and MHW(H,W,N) = 1) ..
        sum(K$(KN(K,N)=1 and Hkp(H,K)=1 and Wk(W,K) = 1), QHW(H,W,K)) - UHWN(H,W,N)*yHW(H,W,N) =l= 0;

$ontext
Equations
    NumLim(N)  limit for number of heat exchangers in subnetworks ;

    NumLim(N) $ (ord(N) = N_index) ..
        sum((H,C)$(MHC(H,C,N) = 1), yHC(H,C,N)) + sum((S,C)$(MSC(S,C,N) = 1), ySC(S,C,N))
      + sum((H,W)$(MHW(H,W,N) = 1), yHW(H,W,N)) =l= Nmin(N) + 1;

Equations
    LimCutH(H,N)  limit for heat exchangers for hot streams
    LimCutC(C,N)  limit for heat exchangers for cold streams
    LimCutS(S,N)  limit for heat exchangers for hot utilities
    LimCutW(W,N)  limit for heat exchangers for cold utilities ;

    LimCutH(H,N) $ (ord(N) = N_index and MH(H,N) = 1) ..
        sum(C$(MC(C,N)=1), yHC(H,C,N)) + sum(W$(MW(W,N)=1), yHW(H,W,N))
          =g= ceil(QHTN(H,N)/(max(smax((H2,C),UHCN(H2,C,N)),smax((H2,W),UHWN(H2,W,N)))));

    LimCutC(C,N) $ (ord(N) = N_index and MC(C,N) = 1) ..
        sum(H$(MH(H,N)=1), yHC(H,C,N)) + sum(S$(MS(S,N)=1), ySC(S,C,N))
          =g= ceil(QCTN(C,N)/(max(smax((H,C2),UHCN(H,C2,N)),smax((S,C2),USCN(S,C2,N)))));

    LimCutS(S,N) $ (ord(N) = N_index and MS(S,N) = 1 and QS.l(S) > 0) ..
        sum(C$(MC(C,N)=1), ySC(S,C,N))
          =g= ceil(QS.l(S)/(smax((S2,C),USCN(S2,C,N))));

    LimCutW(W,N) $ (ord(N) = N_index and MW(W,N) = 1 and QW.l(W) > 0) ..
        sum(H$(MH(H,N)=1), yHW(H,W,N))
          =g= ceil(QW.l(W)/(smax((H,W2),UHWN(H,W2,N))));
$offtext


Model TransExpa  / Obj, HeatBalH, HeatBalS, HeatBalC, HeatBalW /;

Model TransMilp  / ObjYN, HeatBalHN, HeatBalSN, HeatBalCN, HeatBalWN, MatchHCN,
                   MatchSCN, MatchHWN /;

*yHC.prior(H,C,N) = UHCN(H,C,N) $ (MHC(H,C,N) = 1);
*ySC.prior(S,C,N) = USCN(S,C,N) $ (MSC(S,C,N) = 1);
*yHW.prior(H,W,N) = UHWN(H,W,N) $ (MHW(H,W,N) = 1);

TransMilp.prioropt = 0;

TransMilp.iterlim = 1e9;
TransMilp.reslim = 1e6;
TransMilp.workspace = 2000;

TransMilp.optca = 0.99;
TransMilp.optcr = 1e-3;


* Start solving LP Transtripment model with re-calculation for cooling water outlet temperatures

* Solve LP Transtripment model for the minimum uitility consumption
Solve TransExpa minimizing Z using LP;

Time_LP = Time_LP + TransExpa.resusd;


$ontext
ind = 1;

Loop(Sol $ (ind = 1),

* Solve LP Transtripment model for the minimum uitility consumption
Solve TransExpa minimizing Z using LP;

ind = 0;
QHWT(W,K) = sum(H, QHW.l(H,W,K));
FHWT(W,K) $ (QHWT(W,K) > 0) = QHWT(W,K)/(sum(W2, QHWT(W2,K)));

* Determine whether the cost of cooling water needs to be re-calculated
Loop(W $ (WW(W) = 1 and QW.l(W) > 0),

    ind2 = 1;
    temp = 0;
    Loop(K $ (ord(K) <= NK and ind2 = 1),
         If(QHWT(W,K) > 0,
            temp = ord(K);
            ind2 = 0;
           );
        );

    ind2 = 1;
    temp2 = 0;
    temp3 = 0;
    temp4 = 0;
    Loop(K $ (ord(K) <= temp and ind2 = 1),
         temp4 = ord(K);
         temp3 = temp3 + sum(K2$(ord(K2)=temp+1-temp4), QHTK(K2));
         If(temp3 > QW.l(W),
            temp2 = temp + 1 - temp4;
            ind2 = 0;
           );
        );

    Loop(K $ (ord(K) = temp2),
        If(TC(K) < ToutWA(W),
           ind = 1;
*           FCost(W) = (TC(K+1) + (QHT(K) - temp3 + QW.l(W))/FCpHT(K)
*                        - TinW(W))/(ToutWA(W) - TinW(W));
           FCost(W) = (TC(K) - TinW(W))/(ToutWA(W) - TinW(W));
           CW(W) = CW(W)/FCost(W);
*           ToutWA(W) =  TC(K+1) + (QHT(K) - temp3 + QW.l(W))/FCpHT(K);
           ToutWA(W) =  TC(K);
          );
        );
    );

    NSol = ord(Sol);

    );
$offtext


* Start solving MILP Transtripment model

R(K) = sum(H, RH.l(H,K)) + sum(S, RS.l(S,K)) $ (ord(K) <= NK);

* Determine number of subnetworks and temperature intervals in subnetworks
Loop(K $ (ord(K) <= NK),
     KN(K,N) $ (ord(N) = NN) = 1;
     If(R(K) = 0 and sum(H,Hk(H,K)) + sum(C,Ck(C,K)) + sum(S,Sk(S,K)) + sum(W,Wk(W,K)) >= 1,
        TN(N) $ (ord(N) = NN) = ord(K);
        NN = NN + 1
       );
    );
NN = NN - 1;

* Determine temperature intervals in subnetworks for hot streams and utilities
Loop(N $ (ord(N) <= NN),
     Loop(S,
          ind = 0;
          Loop(K $ (KN(K,N) = 1),
               If(Sk(S,K) = 1, ind = 1);
               If(ind = 1, Skn(S,K) = 1);
              );
         );
     Loop(H,
          ind = 0;
          Loop(K $ (KN(K,N) = 1),
               If(Hk(H,K) = 1, ind =1);
               If(ind = 1, Hkn(H,K) = 1);
              );
         );
    );

* Determine existence of matches in subnetworks
Loop(N $ (ord(N) <= NN),
     Loop(S,
         Loop(C,
             Loop(K $ (KN(K,N) = 1 and MSC(S,C,N) = 0),
                  MSC(S,C,N) = 1 $ (Skn(S,K) = 1 and Ck(C,K) = 1);
                 );
             );
          );
     Loop(H,
         Loop(C,
             Loop(K $ (KN(K,N) = 1 and MHC(H,C,N) = 0),
                  MHC(H,C,N) = 1 $ (Hkn(H,K) = 1 and Ck(C,K) = 1);
                 );
             );
          );
     Loop(H,
         Loop(W,
             Loop(K $ (KN(K,N) = 1 and MHW(H,W,N) = 0),
                  MHW(H,W,N) = 1 $ (Hkn(H,K) = 1 and Wk(W,K) = 1);
                 );
             );
          );
    );

* Determine existence of streams/utilities in subnetworks
Loop(N $ (ord(N) <= NN),
     Loop(H,
          Loop(K $ (KN(K,N) = 1 and MH(H,N) = 0),
               MH(H,N) = 1 $ (Hkn(H,K) = 1);
              );
          );
     Loop(C,
          Loop(K $ (KN(K,N) = 1 and MC(C,N) = 0),
               MC(C,N) = 1 $ (Ck(C,K) = 1);
              );
          );
     Loop(S,
          Loop(K $ (KN(K,N) = 1 and MS(S,N) = 0),
               MS(S,N) = 1 $ (Skn(S,K) = 1);
              );
          );
     Loop(W,
          Loop(K $ (KN(K,N) = 1 and MW(W,N) = 0),
               MW(W,N) = 1 $ (Wk(W,K) = 1);
              );
         );
    );

* Determine number of streams/utilities in subnetworks
NH(N) = sum(H, MH(H,N));
NC(N) = sum(C, MC(C,N));
NS(N) = sum(S, MS(S,N));
NW(N) = sum(W, MW(W,N));
Nmin(N) = NH(N) + NC(N) + NS(N) + NW(N) - 1 $ (ord(N) <= NN);

* Determine total heat content in subnetworks
QHTN(H,N) = sum(K$(KN(K,N) = 1), QH(H,K));
QCTN(C,N) = sum(K$(KN(K,N) = 1), QC(C,K));

* Determine upper bounds of heat exchange
UHCN(H,C,N) = min(QHTN(H,N), QCTN(C,N), max(min(FCpH(H),FCpC(C))*(TinH(H)-TinC(C)-dT),0));
USCN(S,C,N) = min(QS.l(S)*MS(S,N), QCTN(C,N), max(FCpC(C)*(TinS(S)-TinC(C)-dT),0));
UHWN(H,W,N) = min(QHTN(H,N), QW.l(W)*MW(W,N), max(FCpH(H)*(TinH(H)-TinW(W)-dT),0));

* Fixing utility results from LP transshipment model
QS.fx(S) = QS.l(S);
QW.fx(W) = QW.l(W);

* Fixing heat residuals of end temperature intervals for all subnetworks to zero
Loop(K $ (ord(K) <= NK),
     If(R(K) = 0,
        RH.fx(H,K) = 0;
        RS.fx(S,K) = 0;
       );
    );

* Fixing binary variables to zero if not in the subnetwork
yHC.fx(H,C,N) $ (MHC(H,C,N) = 0) = 0;
ySC.fx(S,C,N) $ (MSC(S,C,N) = 0) = 0;
yHW.fx(H,W,N) $ (MHW(H,W,N) = 0) = 0;

yHC.fx(H,C,N) $ (UHCN(H,C,N) = 0) = 0;
ySC.fx(S,C,N) $ (USCN(S,C,N) = 0) = 0;
yHW.fx(H,W,N) $ (UHWN(H,W,N) = 0) = 0;

* Solve MILP Transshipment model to obtain the minimum number of heat exchangers
Loop(N2 $ (ord(N2) <= NN),

     N_index = ord(N2);

$ontext
     Loop(H,
          Loop(C,
               If(MHC(H,C,N2) = 1 and UHCN(H,C,N2) > 0,
                  yHC.prior(H,C,N2) = 1/UHCN(H,C,N2);
                 );
              );
         );
     Loop(S,
          Loop(C,
               If(MSC(S,C,N2) = 1 and USCN(S,C,N2) > 0,
                  ySC.prior(S,C,N2) = 1/USCN(S,C,N2);
                 );
              );
         );
     Loop(H,
          Loop(W,
               If(MHW(H,W,N2) = 1 and UHWN(H,W,N2) > 0,
                  yHW.prior(H,W,N2) = 1/UHWN(H,W,N2);
                 );
              );
         );
$offtext

Option MIP = Cplex;
*Option MIP = XPress;
*Option MIP = Gurobi;
Solve TransMilp minimizing ZY using MIP;

Time_MILP = Time_MILP + TransMilp.resusd;

     ZYT = ZYT + ZY.l;

     QHCN(H,C,N2) = sum(K$(KN(K,N2)=1), QHC.l(H,C,K));
     QSCN(S,C,N2) = sum(K$(KN(K,N2)=1), QSC.l(S,C,K));
     QHWN(H,W,N2) = sum(K$(KN(K,N2)=1), QHW.l(H,W,K));

    );


*display KN, NN, MSC, MHC, MHW, MH, MC, MS, MW, UHCN, USCN, UHWN;
*display NSol, FCost, ToutWA;
display Time_LP, Time_MILP, QS.l, QW.l, ZYT, yHC.l, ySC.l, yHW.l, QHCN, QSCN, QHWN;
