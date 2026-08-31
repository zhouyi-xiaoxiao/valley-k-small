#!/usr/bin/env python3
"""Independently validate the frozen role-10 operation-model v2 candidate.

The semantic validator reconstructs v2 from the immutable v1 lineage artifact
and independent literal contracts.  It never imports either builder.  The
optional whole-file SHA-256 gate authenticates installed bytes only; semantic
validation remains complete when that gate is disabled.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import lzma
import os
import stat
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Final, Sequence

CODE: Final = Path(__file__).resolve().parent
REPORT: Final = CODE.parent
V1_PATH: Final = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json"
)
DEFAULT_MODEL: Final = (
    REPORT / "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v2_candidate.json"
)

V1_SHA256: Final = "d0e4abd040865863f1cbf9768d17975f4fbd4310f47eda87d9878bd4fffd6109"
FROZEN_MODEL_SHA256: Final = "ac0c2b185be75f0ecef3e331fdfd47fc674ca151fa6b26600aff9f789a2f8a6b"
MODEL_SCHEMA: Final = "encounter_continuum_c1_n0_role10_numerical_operation_model_v2_candidate"
MODEL_STATUS: Final = (
    "RESULT_BLIND_CONTRACT_ONLY_CANDIDATE_NO_NUMERICAL_IMPLEMENTATION_OR_EXECUTION"
)
V1_SCHEMA: Final = "encounter_continuum_c1_n0_role10_numerical_operation_model_v1_candidate"

SOURCE_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_source_v4"
ROW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_row_v2"
RAW_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_raw_interval_file_v2"
SEMANTIC_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_semantic_receipt_v2"
OUTER_RECEIPT_SCHEMA: Final = "encounter_c1_n0_killing_factor_geometry_validation_receipt_v3"
ROLE8_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_raw_axis_formula_request_v4"
ROLE9_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_stationary_integrals_request_v4"
ROLE10_REQUEST_SCHEMA: Final = "encounter_continuum_c1_n0_killing_factor_geometry_request_v4"
PLAN_SCHEMA: Final = "encounter_continuum_c1_n0_roles_8_10_replay_plan_v2"
PLAN_STATUS: Final = "RESULT_BLIND_PRECOMMIT_REPLAY_PLAN_NO_EXECUTION_RESULTS"
RUNTIME_SCHEMA: Final = "encounter_continuum_c1_n0_roles_8_10_implementation_runtime_closure_v1"

MAX_JSON_BYTES: Final = 8_000_000
MAX_JSON_DEPTH: Final = 64

# Independent structural transform from the frozen v1 value to the v2 value.
# This literal is source data, not a digest oracle: it decodes to a recursively
# typed replace/dict/list patch and semantic validation compares Python values.
MODEL_DELTA_B85: Final = (
    "{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;TO#^wOs%`h=^i0EdMtnmjnRlSA1fz;c?L}Thd&YZSceLt5si$-i2sglh8ISV)vpu>V6{U"
    "TWZ=2F;N(a96Nt)O-xQ(b5&31F=x5U^eezoDN<71-R6b;6oW##O=E>r^&%xkrh%IDd6Tp>(TZ5!?C#BT9aqBq(L3Blbjw&#PWX3-"
    "FBN;m!SK+1nIdr~^re^4J>40s<G}zM80}QY6|n!|#*9=ga1us#&M`OdI7LI|&#Uom<M2|)V#*ZLC_2kEgZka;q%^h!3~X*N)oviZ"
    "X+U;=XZm;7PficLB4@|o-g<%^aVZ-EzCbYDuw<K86KyfC!%?0MA=8AFAOi<whZ=D;3c8Q9_^rDZng<2a0#d{ANngGFdN+FoeQq(a"
    "<g+pisG!kH={64=9PSTTd$&5CR9sne6Q$DuqnZUFDWRpi2ZhZa)q$r}J8`l6=j_0!19@2FzhQ<S>PP+e5M3T8H$U?$!BvhKyp~*e"
    ">2RpI6S`jpZmF`%XD=xeCx#soA-O1ghJ7|$-TgL3dOaw)9mt?Xz29F!4P(Zin`FLKNSs+d5-Co8uj@aYjn@y$t-piKyY;(4MdOEE"
    "qD+Mf!ac;#+FHv3en)?G&SC}kiUuvqJ-bUYs5*!+)xaF010A#SD%#M!{?zHaJjWcLjISQPTnR&T#O+RBS%Y!OH#Kk+?KxlyMVhKR"
    "E*YWDkl8|T`!VcXlcq*d-NJGSPbYYr=hJ|pG97OVc7Nj5Hv1x_aIwOiuaqKowJx`2+&w=Q16Y#ZG&uT~d*UD28z5>>U?RE-x*sAv"
    "eF9q~NH+*0_*ba5-RKgjU7dVS1xNHh)&}TH(nL|K)x^7ew-W#P-IDa)D=PQXkKF;b-@kxpipM3>4A)q)So<hI`D7L|a+-7e;*7}!"
    "gVI05AxXBPaY+s?>jnE)qm=!;p9MiIrs2^DPwMylvJQxR4>-dJ>j;+}oFXRES>3bXBFhO^;KsRZI?W{S_ddBn2S^P?ZzZPze9g#R"
    "LBW}lA50g{|1nn?O`Ig2bHqrc3i21rz+!b7bW3!ctMa9LO2tG;c3IXRT&I>3ar%f50EKv>4ys5wQbAF4-O{1z>WIY-UtrshH(6cE"
    ";=T2vP!8%&9u9^VqTp9En1A*pxRw#U-0#YhHXHH}Fh=gH<Txpp%Jt+&Z<2{x#9hzD^cf?r1)~XSb0`_ZLU9H&_l>q2o|_H!#i3ZC"
    "YfQW?qpcNj5Vc<rf0g9=ngLPExl-tN6yz7FksF^uDUd4f45IM}pbn`kC;!!jGtvjsxU)XoqVVcNe&t~$t@4s=r1sXN%|rrI#Hp0u"
    "EfE?!|2}5jBR@(TOYu>TXf!gc>PljyPGLSbWSW$*kRc(nryZ-&vV`vDf|x+MLGS9wOgvy%fRFln0`W007?wEl6RW6alJwi+R*-81"
    "%qlB(H~&M-Bf9Oea>yLMn($bLH)fPi4|LK>8n0h^&<l&UHH0TJ;B{6|%7Q$Q_%Y(RFLRu1V@w2s|L80!G}7+ObNc0JJ>I;gU+lC)"
    "f$#Nu*jr|@yM$keUk9VUxVyTbz_?NQr)dZH>-8R~>XZ)IBELlxc-7COELt?Yl1KN%XteUxl1$$vA+!~f^uq*+L2Rij0JohL<2^f>"
    "U0<W;UvlCDWdx9N%@kH7a%ddOEZ1DRi}9n-QsS&u(D}7SRPb7+f;n+F_UK$vCW%+;yQe8H)~l(n`2$24l@FYQ7ff6B3ULTLGF2nE"
    "U3Yt1sH$*~4na1{l>RVP9$2{T$vS#JM@1rlUM&wBJRbqsHV%XGy3XCxMnp%<7kl{gx&|xwMT5<N6+>h*b%iXZk{qX)IbAC04lDVx"
    "x?U!j`Mx4O_>S-pE+yU<eDv?lxVa3klnJvkeEg1U+b8#fZLDC>rTiHa7X?=l(a@qbFo&`osX@4JSPC(-7H~Erb@h96uk|j3T+GI3"
    "JpI?Aq_O2robp^^X2q`U*Q6;}1+gpKyebjrJSSp^5gax9x`A97Vbm@uZ+CJw-TP8LV2K|RS(Q*YP%&QyHfIBp@3@uV(+M!=JgN%k"
    "hfAkpdp?0=7x}%w8urXQtuKS>2!XU{aR=%#x?BSLq&R9jwPeP_xL}K{fOmVSx=!W!B|fQ1CJAG2<^ID`_7tOxK~iG+52oEPJh>#J"
    "aJ5Mb;)RmSMVhRoauO3tjLGS!U4Ekp!&$d6mhAmWMPWroBGcEa1R0+<bd&5uIU|B{`s#wjXlaikC}S+3$EebB)KtBa;J&-r>!U6@"
    "g!ldLhC$5kOs`ia&cBNJ@CeGJad6$XAUqp{?-U04?{vh5Co55F$B?_$BMLs34Lg~Cz#&Ed3Tvo#XoD~p#-}`pq3bJzJ!grGra=P{"
    "`yBK~oyt5CGBX(b?VK0p=6o#bCvG{ZFK<oK-fq46UoTp>$To^H3-7b{I!G_gG?{Rh@WNbFQY>fl>>D%i=0Y&LE#N@%PQ57PUW{Yx"
    "xDg?eIq&-t^uUSOsdF9F3)$#*lMnO{SaT^t+>wrrv0SK)3HL!*i2k7O32{ORMb4u2dK%5#-K=s$#x_i`-~&-War3ft+1!uZr}B>?"
    "Ub2?-ItW2)vk`y{8R@_xqyRJVJ#10`08Uqk4T>He&sUuUJ0(f4BKQ_Vgvf9xB*Eu?y*;!E%)B?L5xpgE%IWMBOczr?)g}V+lESf}"
    "^IB&lMn#%)qn<1Kd76_{fXbKpj#9WKT)1?KKcIk_QSnoo)EkK<H|R`X2`Hi&vz9nHIGN0Q^Qi&SglP0T;u^r#!5veUs?Q9uFFqvI"
    "Y(nW++tU{TAbya7P2MF@vky~E^FDtg!2&*U%E&88%TnS0;iAk*K}14Jl`MARK%<IU8;)E-L(&jB^BeWUabQYoql@b_ybse4KdCrh"
    "yrLhO!F3MGF7V#kON>~>%z$;BuYbHA+KP8^(Q?DJ^beB~YiaoNe(-L@mNFq`FGU`UKovuB=Mvj+4FH(@=(%S46;CE__>QeU1cWUq"
    "EzgOi9EGbd=3iwhxbdiQ8!tn{OK0K=jHzCX0Td-QD&hTYybojSsPjHk0&_qPl1#56a!L4la|os%crf#^&@KE?;;HTbCnvJvjdz!?"
    "{M4!5kBF({2kP7a=1R>VL?Zaix~>vPo|K!K(9Appp4JJ*+Wr+=Jt6k|#~Owp&@^VKmSVx<5;J+ekW^Ay|3vFNRFl-051Gq8^n*AW"
    ")bwE3i<`{HY=a|MBR7r&e4SO4;&f%JX?wdGsZ?$opad!+su?nYLKLIm=UpVp>rXtblSIeSu@qN9-3&HXHJ+pNzg3+pjMKE8qDGdq"
    "b76~RObfm(ifrSdKDhLc<v~XgiGXdEyHs-qn4GqBX6n4roepiTvf$V_8Af~w7EeB#d@Wk*3Pd60uy`S)Jo0W>?)6V0ap@C+e?mLE"
    "9IBjTKUQU70k$FQxk;)-o&4o>IiMjNYNPD3ZAi6pk_{mW%BaCCJ#{9DlvwGZGDBWsSb8!$>1qqOTn}EU|4RUWc8pTfOBi+*$nl3f"
    "%4r-t%V<Ezn{`Eb#O0gN%e?_}whI{TKcnWIW1K=!2O{K62{&$&lzkY4vELRDlwr@UDNrjj8@IoezJk^%QeH&_^TXv!>=(1I3egOK"
    "=fb#YH3~If(May^M3n6}iusDOy9bT#u?hPV78xs3d>d{%XHY0ZX4rIJTNK!U+7l~nU_)%augeQ~>XhFAmk^6vwG}w#2$M8M#M@~#"
    "7=2V=>Q9gp=3{nFoBP*$D`YOvg@-Ohixj78nACcr1m=)`Q+r!rl~X5QNE^g^n-Ly<qEq3fNPt)3erj?d`7V9bQ=jE}W@4W-Bm|P%"
    "?fZSXxDuj$sy}!Km1D7by&R%pkh#+iP@WtQT(W{fpLM%*WUu-l@`gx0B66aQuDCr-3+~>@ghynjX?|@0Eru*k+=&KyXnwCnnHU~+"
    "Y{&|Z5Rb?}8L|03tC>-JPw3>}i%39FI&c4aS}hYvw){n?+e2EyDik*N9SjW^1oSAm4L+-LErl!y&ByNeO8jSrH*{J(TlP=n1TY!4"
    "G3!jco3?-^0=;VsyU4)hEY-nM=}7blD?Y9ODThiFb$-JszY7PpsU|^f59b{#NN4kW^~GdOgj-a`7Q)0cr4bu|UO-@D=d<?I!?b1k"
    "a-)GBIa>SA9jgQi0v*glq{=0m<oY`ANDN`RGsQAiS08hfSe#6bcm2Y95qRg@Xw0e~YWyDM#-_&gsl95T6;q7xKC5-PTo#-}0+pQT"
    "owtNoCs1qnk4+%6yR-c@3>mP+$g(9jJSiH6oJ^L`HTLfw^i+N1P!0^#+WAw<#=)zvE82-SS0PH5uy@x59>f!wxv_?#{ulJ^=8FYH"
    "R<?m^?LDvzza0VcpHz_LNDph?%?g-_3#AHYIsCDQb?fG3O4ITYhA_8j42izL9#62C|Hp3#QO$$6P|!V>yQ2Ztt^hpJIBC(SC-`Z3"
    "M_gU*#?V{%7(#f7YkVn5ZDP=-|6yYYRB&~4wz&VkW0C_YYu?P>qFY((V2RzQ81)^R0^e0S0~(AT*@3M`YD?EwT~d&pyW(=VTuH!L"
    "cmu2Ba4^e8_F*eDRjRx8<y7oAEa%uTh2;8QQ$H+cD#E49(07V#ZdEJ8ebp^eT7{-UuESS_{V@QQQ@gjlVIX2mBL%KRb_73&k((M`"
    "nJKJA2iH9HrV4~(TF5b;PYo;c-#oH3>d0+Z$e6Uul6@AVBFCVA)|059+h$^JP;H}|l{N=hQs28GosodCc0fe!Z0E{QtVxDcy01@t"
    "_6s;d@3#z4k97NKc!jWIa~2rAYW=vW(~RX8@F^PA0s%<t1~@umyXg%uHZzOC?g#?+_M%h{ITBW()z-tQU7u|U?4Z@Z60H+%i^UhZ"
    "pPaGuuR^!CFbvzy)@3XXK6GtV?t6y7>S?@`g|Pku^-H&lwb~wuyBObvDM4JQk<<a_kF9Run}EzUOc2zVW4K3xi3}(;o<Ii+M`<ct"
    "DtJ9RfF?*Y?~lOe8p#~N8?p?xnF_o`WbIKMz=uxuVei63F~!&?&O~)$O!jtR$Y$Tzg{5G=DIX@3e<1`@TQB1)VkU5hCn6}dLWgn2"
    "0Flsc^{LZ(q)P=%s&MrudQVjn%P7~oy-%7!($8mu60U2r+EMhQok|^p5Tu^?k#kjHb1+;o<n2`SfERTypTjHW(7y}BeS~8wcpO(2"
    "lXeZXWqK_jk82M0wjs>p+O!Mv^5r&~9e}<J&oz~*;wt#H_RgyvjLYs)-*F#tIaXI*6UEcXh%+JX%<Tu2%7kMI{QH~nF8}O!eQ#g`"
    "($f*_w)mMGCzA8_zKuorj<JVceDftd)JJb-C0m~ZwZ!;U6M|)GD<`eUa}yB>>j)#44%$Fnh+D*_GQGMH%|4aBJP;h<4zUt?LB~#R"
    "0tsSpQ#ZMk3~u!x!b&c|6_X;gdO2tXY(YDO=cdZ0xN-0_%j%qV5Jj1U1ADV5LP7a>DB~*#RHh7@h=z>Z=TCL+<tnKf*YuEVe{r$l"
    "BOdHCH9-O%7k_CGZqCR8%siO;xd5~+`P$ykqWEcSlxxPim=U}!V;c@DCUwBEVjgyi(krO3#E4)vfaMg#EMn_*K+2dRfRE@izLqZE"
    "74}lCG0X`BI00hiSJ!<$bFVT8JM<*Yinl3sX4jn37~<~TPBKJL;gQ!6VEeZi$5+}jzM{+ChC(J`^rjaCKao`S-NwcP@!~}64*l~Q"
    "7FgUrh@l+P7mY7)q%2F8xIZqdPS`?-WVoresw_VurX|I=PNhXG<JHlxWh5*(aE{aLw)yp&e`%*+=ED(`Sp=U8%}(P1MpgIB$XY_E"
    "AUYSxb_J&#Y!m@rDr!|%1l5VZoaZfR3=kpk;<%j>gRRAucYXNn+brS%uwc|i<~#lC8mTSXWTC`>yIB<<b#$b9lo6~7xJi;Q89=vd"
    "Y%tvwdv#P%*iXyunS9~hZ0k(S?6vJCiVQPT+<n6vGrcUf&pKB4*j0sDGW&0|DfMr#9V{YYVGJ|sPGyLR_6V-Pgytb8`R=jqNoqpo"
    "r_`u2-kgUrZBu`LoR9O%C`J<{A(2vb8(z=$5y_>ya}ZET!?oW*^>GN;nY`I<E#*(XeUduF{?A3IQoi1kj^4$!A$rVAOrw2u5JzYu"
    "kF6A0PgsNZE!<ehoc;wi0`7d}@=tS|Bvf%G{K2O>W6Yqo*YC<bIyVNKb!4)p3S;#MBok@Rj&{g#<wPjR)|FImQ3;!VmQo(x;({Gg"
    "_tR&%zh21exVNl`<M%6mbNRSsow!103a;G-ZW$Yg1GRd5OjcOWUIHb`i`EWAd(I$o=1IIlyWseiVANjbByC}?8D(YXY%CRrmJO->"
    "ko`>ySMTB}C9K4?UZ!#j#S7P%%ST;IS|)JUSFKuk=5K9m?p}Sgz5RX}{M@`5faM_w_``AWK`20nW1|`{inyaQB0W+3wZND%DhSu*"
    "$W(gsG$k^JpZOl*N@L~rkm}&)gLR-?2Hgex3ri8lwo~cx$k$FVOL{X*y{3?OM(BEl&X~C`);J<=J@ZE~*p#8k*;OhYeeTIKne9^}"
    "q6P=S2EL7|zsHQ-v;uR$Jho49MQJ>zp`8zj^R&rhb8@*SCK%e)gxj#RCLO!`U{Jqteqr8UnJ4<1A@8kSk8AnYv|O;y&Jv<4-(+A-"
    "5L_QA2N#?|r9jDm)A+azW~tPp!W?}ID?g4;=5aFOo{U!6<s{YL1eE-lwMt9*n{rpH#<OZ4gZ`wC^AYpqS!Sa)<26d>JxqqtUC6jE"
    "hXn}sxkR5du?x_v{1^8{rubx3PqIqC1|ofWPX%8_=Cm0$knS5tZ}=`ZuJA)X8KLW2NN9&WhCqiiLf$G)Tf3)dz|Oy(JiKyw_pzby"
    "AGv;&5eh1%O@y}9Xq>BMpKvxx=l8Wtok3fccMk(D&PDEiCy)8_hSm>bD&|M&a!uo>HOiEa-p4pFQqn(+lO&ALExt720$wWb+-?}F"
    "4JB94_k&6v0b5*wsx95Kv6A6YGiBWG<WEkxNDey&UR|<PolJ89hZ3Y?4<8<ii^@#>g>zyGHkZU6g9rHDVnx+Mq_#Qi;<>RK&+-z0"
    "T#y!*GMIoc$0VFj_}(JYOvm0nX6(Fq^^0mTM?0#S6DYU@t^>FCk+p}%HYozAPFM?9Z^elpxynLP+bnN{n32a$uc~NU_<!Ms<cMyc"
    "Uq*Y2*8e?uuy~Mp0L_v*@b$U?<`PH@F7^6IyZM>jT(E1QX*lexQ&Bq!5D>-k<d?zDGcH(g@4-mozpA?A&Ln;<NDsm&_O=u5^(HsL"
    "Mt3zUEWF2^p;%B?=@U%-VJoNujk7jG$vU~_865xW4O2zLB}CXw%IEML2AII@PF8%9%b==Z-uto2p2Y6iHf#(g87XW!Wk1KH;#8J!"
    "rp&LJEV4A)PudwJDV}<FQiVCNl;{7QPIg<Ev<2_0q}^&Rf<7G<0xDG-7r)KVo+{Y%=+F(c&Xn_+a9j^@0Oy+%IbZ;*7oiNg%GwyN"
    "Ko7YvnW!#Pbm<fjon#&5d#D5LP~7S6s!(HW6xD1I0-D;Gpmys&;hbuzeK<C0Nr=E=Ni?wFd^m8$E~gUIP(@0c@;NEgx9_=UV*ro!"
    "q9+v@L@r$++OZ+eje~o&jGJZx^OT&pjn@xu*6f+QbDl$ZWq9C#n90(rr3Ync;K1%-T1aQ)&YHzm&QbF*OZwW^$=&$oNcU(2?<^^g"
    "ekvWl#^DGV8^H69<<ENg_H-WYwfAmtGJAf()-$0(@G&)Fax-4t9P)-Qxm7qm*YxTFK-J~y6^IxhhueuehTEz=iXv+O@~b4!CI{Ls"
    "#{u`Tdl1UD%p&K5Pu#`MnOcX;N$mpr|3;8@#+sp!iN5=1|8-PoR<ufH72(h|Q|;3FlCmH;+je9CK5H+^+Xp~j!m!W8Hwzw&^7juY"
    "`v~Zo=?|x>nHwJ@CxFWHv2o^2yL9emG-BS1;riSL@B7QkZu~NTiUcI*;dmp{20Wki#Fnmw3mU9jT2^WWq6HiX9b<d)mY_m9XvRl}"
    "w;mZ)jg0NtWfd!bqqggY*;l+4Ju_47zH6d~3~RR!+pS}dTiVI@F}N@H1*?-g)M+M2;b(iM%|O?hWr&X1my%#wS_(L@KK2EaL8F5D"
    "2y4|3Zr^raZn_aMboTB+Vf~oV7B{LX84tb|o|2>QWvL0WQIEK(B9}2B0V5~*R=m3?Q7S`{0FaopAk%t5YLCag>NFm{Dj({nO%OTm"
    "s-9>BBeye8KT^cho=H>;loirbGg?*%_nZxGf(h5Tn5e+}(e7I@>@^f>@B)PbRAV*hQfE|h{xjGilGIw@Tiw{|7JPuTW1oIyV^LOj"
    "W19s%0YC0iK)?1kS4+ngXX%Xwo43E2M}barG83VuNna5KKUOJG#rN~=7B{YAbI5B69Wo}SN0I?%qde|Z>^uQH5uY%o>h#w!#uis*"
    ">?2KRv<w0e?9GXHnJ`o#%vZ!cN`10a_JdRFCGnExeSo?Ifn_MLN@cF#dOt_poW#ny2=y)8{rVN$^}ZBn=Lud2eHVY{G|HGxMl}JV"
    "Ee|xG@W$n?44|hqID)}T{`2IzY|gXhCGyy6@4ks`r}YWUmUGod-Oo<pU<RRu*wy^q;i7Z7&zD$PxmBC3%L@2a0fPt$2sOJRj8OZw"
    "c5r*6RA|=p%=K-Qv)A_uQ@vzq!5)zGcK&3~g}{kou&G^r4i<nLCY^^E$EJ<<fILz)SxCINO>@&*1JzHeE_*Q%(rr3p+d7;HaBeLX"
    "5=$D|akB^tXcRchWkL16KE8Z@YbXh!lmHK(Mxf}mkvTbSTo#+4__<1=8%n>A_mW{0IP_HM<SoTnkMHN@M;F*Wyw3QLPxT;Ox`KT@"
    "zX)bu4jd7a6xN#vIajFTk}c6bUQhzP15`-!`k%H166R>=Qf?Cn)?ORY-+2IC;-r+SYA^-Ie7BzkR4z1N=w}xb<<HolmiV}N*E5X?"
    "GgZ}}U8!}?sA}pu=Xa@mQg9g2Ibr;+!0Ba_6Ai`ER}UX*QC6+4Vw#h=z;$CHq!so$pAOz3GXCFOH!h1ap!RhF{lE#`u!xs*k$w7}"
    "o`t2vp)&7wQ}qEWfj~-&kGN>DsrHD@g*BND0P7kpeB3TtV9tUxmm0@H)^JpGXKe#hBEkqZjtWncG{4Zw_9e6kbP5SE2!+EQ<yky%"
    "gM+ztzEru+rWiltfAI|lVHOcwyi7ZUz2ByU!eCEO@ek*u2&?AChi9snzN-D|x-?t|Z(s>piyVqckf&bkXB8za7duEat1{z~gQ?Ug"
    "rRE#!pmlSvZAe1o9YrILRg_GlJ1$`n{loh&1>T)-uL>K72UBQ?Jo7COwL-N!8aMQeANoB<10&6$xpd1WFW{x3sV$DchkD>X!3N$l"
    "dygX?r9XG6wJX9HTtbc(gSj$|d!PCntzT=rk{w`{5O>aFsb7S8+6`wu1Sz-=Z<UR|mkxJp?shcVQ^v)b8cvZGW{FS7^G9-Pi=lqn"
    "vtCt-jAft(c?smJJ%!m~=I*(?iclmaHwBgIka$7^m0?BWf$G}+@XnK(@xZCBVYX`tsp(qj=bpFCnocGp{ej{^`R4ePXaaJgbh-h&"
    "tO;mQlmIOuc*%zx+y;~#2ms{IC_5AQXDzC7NF9y^4~-GQ?o$=?v<)ubnij9mDCn2mMQQPC?a#VeENurhTUYd4DIGQLeg&Q^q?2l}"
    "8c-jE?C4mYDINOCE{yEYD!?v<!o?kUCt>|{Rux4DQbWv>ZA;1p&Dh<k)Yd(G>QMmwg2?~ZLh^j+V;h$(FLhG6uF(_AJI>PB(@)!%"
    "qkiX;t!N3L=NNKWuv_-zzt-emo4mTl%z|kqDNX_Oi88ekojOcuZ|<g@9$G3R&D?r5{ea&~7{%T1Gg#^cyE7O^yw06ObOZ=H3SOU3"
    "X__F#!f#2Bw;^cj#59tzmw)q)P8-Gsd?sw_{hEyMv^3?gF>b^H(4}`a^jG6lYIhe#4ZeRY+&3ZK4$k!O9D@Q+_hgbdc&}1M*gF5i"
    "k!6XsWzO^{TXMs<z#J_A4%DW&Lqe4_c1zd{UN?!ae6d}k$B0hurNpH^hkIe_<^Xaj!hU(DtP>boRT{ywBe2yt`rVGvcHx1R?v3x4"
    "yojy;_3Zf7?ij^sbU+Bui9F>V^-2i(Kx24&kFZ%qF3?xME$fGF$7Usv%^#HGN=8GY=BZmf>V;ObbRvc_XDfcnc$TBqjG8mRi4+rg"
    "h1&+BrD*|5{1j)NWu^WWgkbd4Q<whX0{;6=S6-6n$k+0YIsx&9wxg&BZ3~T`*0aaga|9XYpT7Rh6O}hMI><t<gk8c6B@XSJ+w;8{"
    "b{mM#U}<?iqoz|zV!HxgC{4;<27!*#Sf$?v+bAXjJ0T0MvT!A6(-(;>5oQEdN+ZXE?o;mw2(kyOGRMQw`tENl^PJ7upzm-g&F_UA"
    "r(#sK$Oz!<p`E>wwzX`ZkxKuGGoF5#cQR1!Bfc{P-rnUlG`KHaWDdLCMk4?3%P@NfxS*J|duWn8l2+Gaj@s&NcA`?w@}N`yav>r5"
    "*2sq-CybcUvkFfv$9H!Vz39&5;`-<_mr5Xh9__!ta<qk*7%|eyM7YcL6)KF*1rR*6+gy4-Z`guA@-~3=dp%J7vAeUS8;Z3zH)_cr"
    "ln)|_wdQZ*{jeTL0&O|qO=%amZpagAEJ=^eIFgm!hp*o<`>a@DHFW_M+z^Q4^nJg7RYZ$yPP!|jE5Tt?*kC0bt_$Sgx`47Z2?f0X"
    "T{}9zj5uovC|(JT{Z5(tigbHy1p(`T;H>z_EVVHR4_|^Hk9xCEa{IiJ*7dY9v%D~Dy<1v_DXic;Tc-HVRWK$-hXlWfC-@#U7t@vW"
    "jh$*)Lb?qP`GWoW;;MSuhX>oy{+V_-xWr#eZ|vpR^xYw+%mBo}AEp}jN|nMVum2)an%Jz1xI;?#TnC$(j%QW!*(KO*OgtY|#^P6v"
    "I!4mR8Sz^Rb34$&5`(}$_pZp@b!Xj6(_x#d+aA|DjeqBRbcvO=ca$3#_ysI)QJ6pVo`o+Yjv24K4z7@-E?m4e(T9AOK=Kx*+jCaB"
    "k!%-(hrluaF&ce53C=UzQ2Qise<m%x;Vibc04K8D0S&XVgZb-CC!e3_r^_xp0K_DkC@xx7FUvc@l#ug!Dg<P9msQp9&2h2hR?^?5"
    "zBQ4_u>zdg+^kFb&|SuO|7M7hWHEMGY%UVDl^3&(AI^?(ChkDa6Im-L*{zpzn`__k8GX%ejGikPtXt2Y4GZ+r5u@yRh+J%sEK=O("
    ")czl{Xov|LNt>x=oK~XilNP$mik$seks(;M@^D@0X|S>D=<nITP#Begb2LncfmDl|Sk9F<eCbW`MSA#=wv3<)$m3MFW^~5bF~b*_"
    "Pg&*NZD;1sEW$y<jb^Zouk9+&=6r`^!F-;}o?nx)#^yR|3TGA!bmu=1VboHNqV~2Nmw!PCYm{h05+!}`-}|NM8xUhR7gSaZ+4@e>"
    "Ae%qn+eqcwo_&yy@c6)v$fTRR=Rud{fgnE0sVo@<e)eNJM^VF*%r>AMHO951UKNWxcxHiMZo4j4nf)Vf4YyLtx<?2XXxkCl2@rH0"
    "7QZSa_~{%-leZz`mx-zJWW`qi4RO%Vqpz!nZ!R<{Evt1G?9gKja4yPYAPx5xSL__)-j-H7&YV_Ab-rwl8qRia6?MklQ%QU69=7W%"
    "@Vf-ln;qJYn@+7V;llNGJV_Cgo2%sI;;+F=8Yg>ls@TD|lm^TI>P%VhNkw3l+{^3G5NZF$T*Zn`wBEtrorKcEnv)4I6g;+ZFf6VW"
    "1^z&;AQVx>4u?)7ntH)@TpxZ!yhG*d$e$qBu)|rt1JH;7M*{C*JE-$%YB5PvZ`JVTF_-h#?i(IzLyS$yG7^j<HNA36eu03)72x|@"
    "2FJK|!LX_G1Fd<C{`bV$GxPuIefV!{;YTDXlLCtM7|gb^<(%LI$=HCK;ofpK#5Tg;WQSF>OZ1O+vAk{c(<b1glR-N-{<11^MFq#S"
    "a^F|>7_5BbxgI$sK)zIS^$4~Va0>5k1}Fe}&Si}=9-uT{PwbQN<3qq%VZ6R2Rlr1Zsxc!=V7#6*e)yX@5=gj>^$Tu)9*qs!+UVoy"
    "I{RMN@HYxO>sAWADj9(yR^Chy$5<4Z8v`fCCYvW)TSwDr!X@VRl8}i@%i3}ajc5NAXwNC4xW!P1_ATuwV;>kF8H$s+B|TXB8))Tt"
    "%qrgnlF^;{vz)4+6OPO$!e`|7{0gNK3+OE${vh(nL<QVXGO|G*c1-S7uZ?xnKB~GRc=wU9#1~Oao#wpmml>}zkj~Uq6L_wYYxmL+"
    "NY#q=G#85Y5tQ!)z=B}-2~iT~W5r$xWA{02pT*k~mAVFCtfn|Zo2HbQRTJ&4{jR1o4FiIEB*J{CdVJ1AAzIHNP9L5%HV&0#a#bAd"
    "V<DRu#^O&HgSZ<h7{}0I(i3|f;f6e5^;`A|pTELDqVPU+f~;z*)F6h$n<}=(A!mq2fvDWCXwQi|v;7Isk(P^hH#t-jo*$!j2jTh_"
    "!^Cx%#wMivD@qVHc|yoryB43vZRhfuDXJX9{}MEua4b|_ia!lqUm}%ZV$@$*!Bt9R`a0>Z_x?Jv(Od~zmoqu$A)B`|k8ET8!;c8P"
    "PnpQR$wMZLuL=ML3BF$d8T1%wIvuH)_(G})q6iriSKT|>b|L1oCYaT(FjEL>%byF~mbxj7x_bZ;E52Pz1jf`Z5DM?t`Q`V6Y0}r6"
    "_jD~C_K>Vu7I%OhhsvFO7xoJ^UYUdhUd=j_WIdWcPowHzD3Z6mefNvl#4W?kXVxpys_QGr-+AHbc({3=Eqo}Q5)9{4<-Uj_DIyB0"
    "Ya*XMDv#;F`KM03=1}E$K64%<<%Bc&kX8<-TpG{~(y#B)$trF|s;Z*~nOH1xKO!i+DD4(W@NK$)C3Y%wT!Jf^%9a<-`paTWQb4Ug"
    "r^pU$;3T;DS{Tt2P7pGcL*XeL_EjSVZu#S$c#DKn@T@ZM)@A{Q&H6pnsNs@`5>Y9_YoAmGr%X8VkCUw(ZHt`bZ3+r(sJK7Dbf<e<"
    "QK<)qfX`1eaBYyKoCZo{gQQsN#0J?S7VK_&Uo~PSAsdlfYP2<J$Q;|J?YUn7t&w#aZ4O5ktOQqIX5k*)5!tu&#%3Kzg7jOiB|-`|"
    "N31KD@>09G)-wDe8;ps2if@&_`NyCg4idP}?D*qmTj=nD!FHfN$fBSBi`(cG5BvAC4c+J<P^Q-kv5hS<CG;$c!VClb*(25|A;$sL"
    "CWXJF;svr?4~?~BuJEZ6EMhd+3AT{w2uNRGfVqOO$0mWhNi&0g^on3SZBw7Um%r>9Lh&OJO+1d9(IVmMT~u}SW^PFX)$gaou=5vA"
    "FR%Li7x7XhdxlKphIxZnT(qYpAZup{Xd#lN&_Ivlc{?(@Z}4nO#rw!_(m0SbB1n<4ksM62rvrYJ5iXerk`{>jPFYf8%Wz*^*5&ks"
    "x_s$ofiGt91@r7eNM$bPnCg^F_Ct8BWNOkf?2v>#XDUAxAMs={Y7IdByJ|(dnz2;CBOCEFfIK|(iG)J)4JQcsaD5;^N*C@eC`Z7I"
    "AK%mTsfjRQ#9ebHHGD}Cfu?)%vxKyf#fat}SCZdsC^?yE!hDTCsT2Fs0EZO-u%1MAT;@)G^-n0<)f<Q0fJQMy%W3|!aHACdh0_dD"
    "1k~2^|G)HBJUX4_nIOX^ZQ_^_*z|e;X*Uzh#R+i7!$X@XspBVrASn4nVzjZXoYpd@V=#9}PvOLj<Z;)`<1mA7gRgOMw&zu3ELpl?"
    "Mb!9$=U|{xPl$kT#8Jq{6e#MH<)G>4jvWfqZNm?=i&}^u)w*`q^J{+9!pBymHGQjFoH2RBB@fDIf02C@^}ON`nYiyoR)VXR{Nu+Z"
    "N_|YmDD%%fy>LU3`j5UVrf`<@%R>D=P-;tiNdE}~Rq7ib3Sv!@5+x->DxHr#WJP^uqlolAHi%z}m;^Q7^iIS61daNBm8WkX{W72>"
    "Ta9R{o{C8Up;-RsQF{jHP&gVxlc<>%`om72EgC%}U-%KZ)xb}SqcX6Howf-C)0p#rN$;e)klKnmbB-&&QV??Ma&>)Sv_3)hNe#S{"
    "*C$3Vzg%0rU*sOISMNU?_zg1{uE&gMC9^`2s>%r*#!Gw;ZPHpf7ez)RCGI9!5c3-*OfW63s`mq!b7&&0^jMN+A0x|Cg7Atj$i-ms"
    "f|;UNSJhCSBvBf(zl$LVJuD5hfHi>>0W6Elz~K{`b=mPEa}VshZ7CG?Cgn%m;DK4Q=Qb3Dd8#>p+SCl1(vbs0*zK4OD_iE7NBz->"
    "m$BoNg9l7nZfDL)R?gln;S>=q_VOqf(Y|+X3p`drG1gJVe-gkFU4xU}`Bw<O`A9EPBzMTqDwa%dy6OVne96R(lER*ra0a_i781*`"
    "FCbb9tce=zhq)DuC3yQpHi6#33C;=^{>t$38#g4=1g_xcWg1H9P$fb{ENL~I69U*+PqSnRh-g=jx}P?b%>eCOn3VFmv6~B*RHs>&"
    "%s*@s&cF9Rwa6_#5YFTHI&dwspncW@(Q(#}(Vp|DIi?y!%tJ#wo6r#z+8g@{@rV=^$KxTx`TEz^C4!|TArlPA=$!Q$3mt*tjfi9P"
    "2l?6RNBPF5w*F{NO)<?J7h?hPS^?od2WVR`>pA4Lf`RRq)5-c}9|o(n)STfqRg8V>RjL|#wit|^uo09du<ygWD}oyo!u}lxyj?<h"
    "gG^$EnY3~Z+l8CzUw8mN1LdXj_x~V*vU7AuMhqr<uy2@7>(28!!E-dgjx9T6g?L557A3_8K_x1WT{w`QQ_mHi@sfp?rPU8WWi<?&"
    "52(YuZHV*6Slz-IzY>p*e5O@Ss{#zX6CB|%kQIJcyok+A&JsyZ_xL(r8kvrfLPfK62=9bDGVcpsOXByR3$vcSuA8@jDA%=CMiAko"
    "z{Me4#!?skEx-t?zrb?WY;86(o)9yy=cN1ci-FwO26foKdK~675PbE3bY{l$q`8v$OEOZuKoe)Cd`Lo0D|r>3JPQ?R@22rHpm6-!"
    "RmNh$YERt~zM>~B^{Y`v+@YYpcY=&wfHVM`fKhz(cwsZz6X}MLncgPWQ&$B?5yM)!=y=lQFLFW;jRWSO2K^p{-;50KaJ#68Gq|UD"
    "fjp#DqVHM^CMy<No?^Z7L-j2aZA=HO=r>nEz$>{hAizr$(nbWy!@yM}4VNYql~{YszXo~Y%~+x!4~Fo49<R<}A;<_Ti`>^c$B+5Y"
    "^-1jp8ugA=$j0;py3<#tk+c)qC$fjfM#tfj47awAh_b{gZ8!rHkm_Q~NlR=gq3~=>qQpYu!3N5KFM5EN0}fH6uq#kIXLfN=J@_CG"
    "ASusT>l`96CYFa{pj?8}0^oYuqt-Ewq51%c)eh+(eQ_yg!72;S0`<~=ehQfek~Id&bkFPS-mL|y1nUK}dSS@G%ySL2+lTCSwZ(0!"
    "_<q-!x33l|#|eWt#|O_VS2lVXn7ytXhB;A}s~7zh1{VR_`>_V<BF{G~Kp_uoE=X#@{cn8Rx8o}pV{=7~B3L|T8(-)_nGCk#f*Ln{"
    "C6C?yB-*>Q1DU49BB%Kvj)X9A*b-MBAn4zAhBUl+P(%^dwAEE9i&ffY!=-E@=n>Ie5}@mOGbwT5cbp^Myjhgdkz&mFNu*JIg1zX7"
    "I!YpWkMA0)uc7-6FD?(ljpb3HNAtxkV;#pTHDrLGdhE`Q_AHW#siefbzr!+nXTV2b3N{^F{%pv}ABK&uz3hohC-KKH<9c1Q@I$k8"
    "P_aYl99wC7gY#lyaw)mmxr$o9oUFY0CSPRvqN3u9Xjs3}X#-JC8gPidn}65UX4pFb<<<Jc*OJ8o+3d#`2ywyU@FK&il+7~OIWH{e"
    "b_&%&Lzrf3)3yXggf{4XWyTayu5=dH_(ar$Ma%27yh?d>0)s&;KUcWp3|QlVwA1cOg6)qJ%(Y>1#aDXKUlRrX#DI&>!IS5jd@{Ry"
    "<Q0|AGN%t!f!9T^pV)Hjk`VdfH@5(_6e}>;rOm-!XMt6_+QkfE4@=YAmI_}xQxxZ00K=+@P2|g!emuTzHQT@9QfR7cj&57{%QAqk"
    "smhibwWBeu0+7qw0YyJ=bJ5Bg@|ULw^l6i!oyLECG^5z2`^D-X*^|AXIB;i4ILr$u@GYuzxrfU!2vPHPZ?qQx0}j`gGhZ}>C=p_M"
    "e3NYY6@;;1)E<U22QJE5FZttNc_0fd@;v`P4cCsmT=JP71EOma`CTWLXOS_&^>V7X+jijg^?F+9U(wjdCplH2Q3Rk8=oa@VHxq8h"
    "7a+iK6vLsb1OnM}&7P1Hp51aqM%rE(R~DTvY-=+WLvcu_=1TZRp3uud+QsE#l$(1eP%M~Y$wq)7*>a(grQp@ocHl|7r^Ie>p+s{q"
    "7Fzu9sp^NO#0=Yo!({f-K%^y#f{|RLW5<42@u$OFSrb<C&`*D9Z;;Of%33|iv$GzvnS$&up)<HDl@@j75U^`A@d7ZH(D~~F7zmC;"
    "04}0lM5(u6E7-^gT;y)H#eNcifvW7lppjjBF4ySp6Ly@`A>u09$Fm=BbT=B<ZQLY+m#N$D^|Q`MVaC17=QaqYlpJ>ImMVf-=Lrx^"
    "<zM0&*>G!4HuR#$4u-+zeUli=t;fLp9}c|LH~t%ZW1E*2Kj)-Ycrhg3O&k(L3<UyJ6s1xhI_d_+(nt7gTdR8+4lfbquK2X(Xpolw"
    "B}7{zM8;9Kf5g=MxY5)nL#XCbm%~L(V!Zr5M|#5Tv1+v$<wYkIi#laVt=$7-(Y>01;Ry9OGyL2efLL}e3Oocf<Wh-ax-q*EvUG`6"
    "lzVC6G?uxOlAJ*<LPJbdmGBq|p9etb?^oH?oQ19)v3vb4V_Y=!-|-5Ti#33Lukt}{;H18(`{1SU-4xG_;dh9`U9=D$!JYulM@RIw"
    "8f~CY40$hdY?E6}xQ=??9b5E^v(R(Iw$2`OEzaHPM4_VqsLwx=?#NLLn#f?uJrv)<00000&-oay%FXW`00Gfu&aVUj2Bkl1vBYQl"
    "0ssI200dcD"
)
MODEL_DELTA_RAW_BYTES: Final = 71_630
MODEL_DELTA_RAW_SHA256: Final = "a7c0bbc31c17d184bb25b6ac6752b1735f649ee68b5df54597d7316c4752ff24"
# A compact second structural delta is populated when the audited final snapshot
# supersedes the transitional v2 source-data snapshot above.  Keeping the two
# reviewed transforms separate makes a final repair independently inspectable.
MODEL_REPAIR_DELTA_B85: Final = (
    "{Wp48S^xk9=GL@E0stWa8~^|S5YJf5;PiSkF<k&Xh=^i0EdMxa1-=$ScRH2vL8BuW-S00|n_I)9Rpk)<#VL@uRwFKQR-&BmRo?Q6Fp!fNs?`m<7G4+nM;a+Y"
    "Lb8xC!{;pv-^7SC;(=9eUvR|0b<eN8K1RTah3Vq>{KHZaU7V2UHe-u4(id~i05Ix(^8RjI9$um`v@rN*B!`|NWr#$M@;^RWQIyIwiFY0s7QzR<)ajV|C=XEE"
    "$<sFx-i-6+>3s*$6N@4-QuK1gm>uc*YH*JCbFY2WYVZ<V2@uOOkf&46LWcTyIvDu%W5jMUp`I5DQJU46p#SAZv#p}l5aG}G_r9!>9^3b@^TDXNB}nd|)y;ax"
    "3S%)dZU5uYn0ZiErgyo?sA$IFR}=v6R15{9OSk}gVYQtEKX{D3DoS^Dy$dA^_IM2tP5N-YN&PlUswr-0pasv|57O*Ce0d#wN30GaZfPeI;kj4i!ZC3A?$c`d"
    "zcW_1g_koxWv&|G7lBehjx<djEk^Kl@NE7a>9y{-p&32-zXi6+G;Al)H<bsxe$i!>seGNhCo%u~Vt{E0Uxvxb3E_L<)?)(5-LGR6oX*v$G$;1DPqnHS)NNC!"
    "+4tTh{l}nE29WpfjE&Ma!st-vYk!BSWpps;Um+xdBXMSfm)M0Xh-TSav1`XEr$wJ$5;S9}#u6UoP75!V)3jBRBk&!uR-+T+%>bz=C^<lxpD?y-c^b=l3JZ%f"
    "wY?mE^o(%(dn0`Q7;h7A{EyvGD5q=jTHOwHOH0q%J$NMaqdZsGVz~$|*b&&n=wTTJ)SuAx0~s<W2+>ldUel`x!yO}1a|COqJf6tDol@{4TZ9o{WAvMHvoWF7"
    "R6BU<m;_=fJ0bI+MKWb-Jb5%~sjB(Tkl1O<+8Qh238H+=yUejD-BATuLgrrZw%)O(Dj;Nhgrz5n(qY~Vbnk4Us+VPCNANhaLcZM%dcO1B*onp{5D$=<{;*8c"
    "V5lg`3~dZ~siBA7Ve{Z&lriE2LX2+4n`i0<WnKHUw47^j1u62a{M+Jj#8}<yKrF)2rP5<rpx$bRc!q=`8ns#+mE4NMZp5s<vzRT@2FL-eqz0fk3_kUfTr=P;"
    "z|zXS*ebREbg~!D0*yN3=B%Uc@J}}&zP^eO0i#rY=aljLPXJ@zo_e)Ya*9S5oTTfwzy9ZBvUG(|VX7_HJ;rfuJLpVM4Qx7ooA?IO`fI7Cew4YEj=JE1!o=+!"
    "5~vak<>Mmuw6$aS%(>R&F^`z#LKwfIqK6?svI%C8%qF_#6~vXi;k&=R)^7alxzR@s5PGQx5@DUZf6=`u4WQ(wAkxQ=+Z9{cX{Sid!<JO6fjJuD?iv&X{LYCA"
    ";i+D)wG!tUT^GWe_j&0R2PlOd11V%{+ByyRwKWry?ef=OjqkXC88l*MfBtAti2dj-^`I!RaX+PCXyC&=OH&}^X^<&}pp68zFoWw^Hdo*jHOI@_R6WZYr&}{V"
    "`w1rlFNW{U?H;a*S4uibwnK9-55XZczN|83i_1SMcm~{l?20X5#Ltx%3Os>wlsbOjr_NxTthCdS2kr2&o%$akTHMt_59ezc6<^L@g$yMvfk*xs0S~u92_(-|"
    "MAqn^BsAn6#?MDl{QY<b%G(DI)u9MgCzsBSuqL8$c*v+GxBFZXY)6~X)66q9M4Gc$yXeC8Yg_0E`QsQX5gkQ7WSee!F3vw>t?vgnSV<1*<FLSAYc<nV*u+uA"
    "(Xty}9b(f%41eByJ!$G$tSszOIbelx`GIhS`Lz4hcntqBT#D<Dp6L>5XW94pO!5^|8SpRlXfo?*|EW6t)hFr32nepcuHymBCPHaJ+LrYALGCtlN0k(tUxlm="
    "fL-wfwz@j;ybeEU9r*_=!FgBt4H^sskb6p~PA}aF6=f>qSyc2Nk0B1J`Q~uJ`Ds96+n_A81p!Fpit^=>Qt2gp`1o&(9$dl!mn`m*6h1nXFBVg*%2T&PbKtGP"
    "K!IUTsrd#+iOb6%8ueQ_5wgyRGI?3g`^51{<N3H2=vrk~wuxT!BMPD!h6}Hf*sC~yg&`SvaO&+5y#nB>VO;`3)1jh9R^lsA5j+)1DyV_|VQW_|-yUr;51nX~"
    "ienrPiWP}^c~N4mlZEVISA@cXUGJQxl$*vTC$nAByZv=duQv|jL^UmDEcy=pj{G^&f;}9fqcdRW_1|_?ykBoZ&N<0<)PDd%?d5x)Yc%+tnKMxXfeEc%Q33e~"
    "zG^~RkULUN_{%<-RQwi0dRbZo@?EQ|ldcWFZLuuEdDd5<YuhlN>B&c1-3xZoA$Bc0X*ODa=z=vaS-?P~fOr<b!UBjmSBRm#eqAneh0I`p26NXy44KHJ0PQb`"
    "N;1R0%X4iksveCrSfk923>N!kC^{*O=*WO;G8GPKSyxFzBy>kogWRy4E5xe@q^_7&X&Nk9H~i)8x*xaLe}4;T*CZO=c8rSa*<$>L0K4ygW4unxFJ$c<87UTw"
    "g1H}@)Gz|q>{*hfuRZSjj>@;SjtIAO`M;f9zQ-?stmPhC-R@SGq&}S^UFm`eHG7|g?M_&;D0JYW!C3wjN!pu%A+J6|Q0NE0ANp1?y%%_F9>;gyqjoZ12FSGw"
    "+BUSOIALoxvO_chX#b|?kAOcB`0pRkmH*<4SHUkIq%2fp6E2C^?TQZl*cZX`JZ@1hV4Ug14-)8IR_tzgl$!dlwL)GNX{KP4elKRMp5v@pu6yTX)I=x-X@8XR"
    "sTw3sFy2M}9ih%Rs~snt)Kx~uC8CA%y|8y1)|FB8>*N)NZZ|+10)6A=Pjo;(iM#V!Xg{6pu#@zu>7XRnhE3fMJX&Cj8xV#0G!7#rj@vAvdDw-NFxR*kWxd>W"
    "&+8925>Y|YU#8dxa*H5*vL@5x)GB8hu*kum$8(lp!%Wy2npr@%?0z@lv0e)K=vHzl6<j7g2863n76GOYxH~rsB5?dS6ulDBzNzvCQg*0#4We+E$IFIN=_Trb"
    "YiLM5ktbb@v!dSgZNp5@1ZkZI(H;Y&A~EOiD>P<HBDz!A*Uj<zwtt-t0)W@65{8@dkattc!PSshvscHe8KRuyjS$_X*XGn8uREGa@={TWXMok@yyB?rY76Yx"
    "Vpo@19|;cT8awD>y7u&P=BTR&&Nj?=4UHECw;U_GH5U|LomE^AUU`&-))P2GT2XV>vw57FN;TdB7q~`re9o=1NZimz$N$ye^nOS5qun(4SE&SA>b(7AhvhB%"
    "nVU$MPV2O@a7(i^W6H18A=Ws%C<x`&*0#dFiY8a(SLuXNSN<VR*U)!5HUFS*eacbD8a#L%6|PqJFebR_$~3o_!>9+ug$>F4Uq8O$5axR&a<=I*RIkwx%;T>&"
    "!ok&jOfQtH_d>_8s``R^LjY+ZyaRJsOlrbY{cb=>BaVcJNPPrpywO0{LsLh1*CN-+GEW(mjR&cxwxc~^O8b}p?~Nt#+5T)DN9#e%SET_!V<w3EJJq5c0O&}N"
    "h)t4p*n-I{%Di@EOl-Px3$4Z@Z3OXCYBPI-mSTZZy!3`uYbQ*66C9F)F-(MhW*>-3Fv)tN;{J%A)amPEf~ctij<qrzk1KHAf3ba+$8u$kKON$fy0n}CAjIJ6"
    "A{SJdTI1bvb|<kIGeTae%u0M>`8qV;^rmb8c_ETq@qpD{m$?hooaKxw8_9BfLCExm)ziX&xmz?&qHOJ;Rrv2<vAknUj;OU_l@=64Hd{HU{RM<n$Dd*v<owo!"
    "v?gge!2B<O#MmD2>H-q{OumKY%ZQv%aoX3^VGm0MpSkge`4>k9;MO{VPJ-MWRB>?=gYO(}7e~}~l_B{T69BJEG;ppR{N1)u{M4;lV@t72mpZ>@KI1txvc-f`"
    "*GuTgSb;n8N>Xny5_E~Y%iwSM+csrqQWz_G^A8B}Ui}E-FAr@bxAgj7ng1t7D3tIY&k{9^Tuky2sWK6>lA5A!cm<<qdpru6rL8{Mh?=Mc@(htS=s97poxj>$"
    "uvc{AW7jPb;1_*!LMZY8ss@&=MS`JYMmBwUQ9+@utyf57t;;~bwumpsU7o@)Ny}`!3?HfWK5w=uErJKQvaT{%`@v$lvrN2*f4X!|Ve)oexTcGbBIxbvRZ=&v"
    "nC<k*4`4TgplLYuQWL#+0>J}tL48mquskrn7uvHj)3OIF!4b#_iYqP)y~mc1cnqr>>PLvjV69-OfX}r79k$_LovVy)uwjJX)wHA$iDEpHI(_g{>4%Zcazx1T"
    "dub+_?f;9a;=!EKbF*1MWb^2tsA|B?W-<ME_^wakph&0oSgelq^vBLJNpS=T^?zr%VBNX&2L_f^wiT)&;6Hq{()i_eUZoks>JN(|Hds$<O2nm-rP}^dKOVqq"
    "$KoJ1{Q6d_C(?_c3A7Kh-tr!VeUx0u>Jk_OK<AbP{3hK0+5|RyR8MPmIO~#qaN_eshZ~qOB=l<0p|kG%1A(jh0Qg;W_`ii2-ezTv&c5x^XMG+QN!aHF0KgAn"
    "#(%00DUudUg}hbq3EnI*JfS|9_iI_&Sn(vmq2Aa9R@dg3?GPwnU3(t$atu*y*U5Ws&<^+~8tMuL2Q^Qld^H3=I8p8+3MA%iey%HQYjT>^@=5Y*g!FQo1q@wZ"
    "pwk8koLQU$Mqiv%vP06vW6<X3J~Gu06AG1rs3cFBya$;qNOSu*OI17%JgDVWY()iyi1~k>*UGok&62qRZvls>vnOy!ZAq+0bm!5a(XDeT*CSPEEMH$8y@Bms"
    "RiLHf-O=FSh8#3iI=Fi_q(R*U(_;rWZ{xwp5LAOeGWV4Z*uYXprESkBR2LBoE7n!bw=sGgdd7*ILeuW1s|Y^*r4i;+6|BHeP)b#7Q(}M`gNrViRLeo?rFnNB"
    "iG^5F0GNZOV{q^I_Z^AXgfQrFk)~Q$w|u4-(Gn>e>NR5}i2t>O;W<=&xj~CBbMve@e6t7HF7z*t=*+>qp;E$pkC^-?m#V)Mf>PjGqgi6dfAWVQ*sc=ql@MOw"
    "&ShT8Cgx~KH<z`?3xi{-c5T!upT7F2F`8Akwg<EzHfh*?0VsTZQ`Z5QrJ7lSZhy-Me?N4yQ%|ONE=S57#D^6;j?27NIkhucj(}2JA9N7ZNdBAzm;5r2t>U<V"
    "?zXUG>fAZd@&Zl)Vj1o(?*J>b8HQYs-^fQ?sM8XELu}Axak|4JjK{7Gypic5NZoXR<DZpF<&)5g-c6kuvqGSZ<d-{By|e63kM?}6o|Zt?=T!n=trq_~HV{#l"
    "!S%P7vw-Z{9b0;*sKn;X_(G76ga|~5{}+?H&FL*g56*lhpuc_z#vvcV{O^vY`tt5CcF#HO#5>1VVUE7>50$55UEx-T;1^?Ofa%E@=Oh6p<=bm7+*dkfD+a@u"
    "$!2Wq9aF2MUpeLO9>dPs0|92huT}*wc#oMYLd*wH2MOM}w%?p@m;aR69iBbE;gi&<LF#_~-PB+z9s@z*AmkjTN#?&=NlNb3RoR&Hc<lhkxI<O^GKpUA?U|L5"
    "#Du*>7OqUH>aP5KzzwZPN5J1xik#ZNU3h$4er#uaQj-+8IzPgu-i&snazs;%#vB8b>x|A%&WcsoihmO0X+pVdl=xpiSA`2oK<u!|Z%Cj0Zg({b^QxnDD1D1k"
    "4?|alR*6CzA12e{R^qC9j><Os{Q3(;I$xF)t+&dCS*=(1qNQ~3F^Wfv3;02aS-64VKzn5G_Suwz0!|5>{f?LE%Dvl-9j6=ozPw?NRy{YBKE2V7#NotQej=_d"
    "L`l@EI2rD35+_`fyBR;%MZW99Pj$*}F86iVUc?V~afF{vi3Ql5!KU*c$}fi2?Ir<5il`FN1Hbr^ck^ne1zFDTX%<BGsP1E0q6T4exF!PT_b1az{7RJH{#L)%"
    "LEPShU|_nwoLjSbT)MVt9Ik)~AID_(K|5PEHwa{WQI>Fy-GhVZ%~!+w_8#i1o!;mh^|%~NThzaNdP>gy^B`jm($MrT5&uCYMH>O&pR%ATz(Wc0&PmRs(wW8#"
    "BK>+aV_5vXghlBCIh6Qok+ZLPK2eZIO%!(pjEPl`A4iVmF4DF|q;e=$avtSi!F+#8Zo4UW@K?+{9lx9Z7K#v6aBFOCZ_p0=Jjm;Yg9-jkLQuiUs9Fsz;(#$>"
    "SzqLLgkbR}<Zy>3L))VD*fQiy^Ii0#wa`|p))eg0C8WK$JFLsfdA&)9-TpKf^>@uIH88q1B{a*Vfee=&gd-*V&tCWFBfE7+FNRlK0_eUH7K+@5(o*%4EvU%#"
    "5I4h^(zBMmmW!TUAWHiufg7Hub0HG$KGiV0ORj6ML7fDQC2H;EP2AI(9F-hxyN>VUZ;m*4G<;X$(#9-M+F6slTo(Tg)m}_v9KF5xem_Ry?-0~&`9RtFnKi#M"
    "X%D&)J|$~p+L-+T$c<+&JIo5-aK!J?^RRLE@AnU+om42rkGB>w?oh;38w|=`ji{^#Os3Xz$8yjz-R)d=5<FaIZjy_jzKqT|X`8bGGJLL|p01zuVevTQ+jEeP"
    "QV<x}2?Sq>&BGxqiUOAD^&$JkPhM5Uux&XR`9E=a?{X^l%%o$hOhB(nI@UM=VN+{Zw2RxUqsvzr(bOnLV;XitK@H=UDa6Njg}}p}d-xnS)yFW!zk>JTU%v5E"
    "jsnlQkxA_0HFPo5qtS-P>a3e|^TV0{|Mr7~Chp^SK63p=q4W#5;!+Mso>Luct8`eCk^lW!5=c?56gClt|9)hWpZn?Hdv->$v=;??kRwq`Hkt%!FUMq2SQa{g"
    "vO3JuJ4C&8Xh;A?N^%W!#xk3c?7=F)AAhcQp{))`oZ^tuVsrAk$9h1e81K1f_eCVspu9O~qGtsnh;$2nq9YBU$!{;v_{J-70ohi~Oz9|wOmMrY2A{-(yB2b6"
    "^3A(}9dL>Ya!KjF_+H6e58c|1@z&WACs6E}5+=uo5GR;Ke;dx^Z7qEs^(rnZO<*hzfo;xTJ0>1$95T6`m0pU-9*H;Cr1p*|uaY$7p5ksnBoShzzdnzq>zAEd"
    "3Q{<xv;5GAfOHeH=te4~<4wcyoOTzm2{<QROVUYYAsrgpXHau2leXNgU4Ti-2_ZOV+hs}<)O@2=;if5O<G3t1RpkxAs-8oN<Z?*g9=ESH`uVtxPv!dvsAT^t"
    "Xj(bEWGWWwt{SZ?C&KzW5d94r_`pAYL?+se8rhEk2^!HSuduSKlC`1~n$<>&2fb-;>;}bp^;lD}!7gsqdWwdh&f?*JZWB_y;FHCAEkI%Lzz0Z<YQ(A8Qd(M?"
    "HM;{or{90(dWgX&$-EA%Z1yEIGphcDd!V0N!dM<vTEcb2Msdhrz5@IlG``z`5vD-N7&K@fLH4RosSdalvZEVi&N1*z#o`<7T)>b~#NRUCM<T;_&cyP*&4~-("
    "cvxBY8W|H!au1OlF=>jM=Ykj3Fp5nF$g8QFZ4jGYNa$=>25_S}*FNVJ7D<fd6H(9Iz5+jQ+)+K?p<W7JO(k9tm`-9WeBYGO9b3Ld{_E$vsZ0{LHiZPPhvZWw"
    "7!;wS7ZQXOUe{-lONPhHQ#j8)WTbNXj~~)4sp#$KAamgbrg_J{NaLGXu-<!jn-J&iS`{OlWu3Tg-4Dyb#-lh)H^fNG<Cu0ajnGqz&x4I8%l*n6aR3b=sn6r{"
    "@b1XfUbq?A)<Ie14n4Au2I2u%Gy&aAj85>lPcRajB#<MQ-GOydI7nLQJR^09g>VOK6bd`(j&y0K`QW@UXS2r4CJ;H2RIspT%sGS)1rw%D#?vw~6a8lL_Fr>f"
    "L9go;=kakt?{t>pZwl)ZPnW24LZnoWIKl&(K!=wAD3p|p$7IMQLTd-Br@4Xt>UY+B2NvTy3J-p?!8IppD@h|-#=Bsw)0Pt7pjF-0`5nb!zI)J{*x_`ns}L8N"
    "+nC$caiw%>XAz9;i}fkm;!AYg6MkU9_#(cbzitKPu<wb|ebxMa%Wy4IbS*#XtIKhYF9%u@8;aMqK)M(aYr^^8g7;GsA=x0~%}_XPY}M27*ur)TK<@-Ho1;18"
    "Iu()m&%{fj6A@$EsDIw8A_t1=JQ*gyMM=r&tz$KLMOM$wY}a-+?`-nm`j}^@GIkV7Xv<{OhH(euqRyJ}b0jV$M|U%mWh7?ss2l=9eKI=$OO2@8-~8P}R;^7t"
    "xuQ?e*aE|LB41k^DE}f3|Br7N#Em$BUzX$cM1LBnL9Ta3>PqazwbbLTOX^0!v#=n6*4`vLxACz&pR05%qtGSh^`94$rW~y%AV#9on4WDxk1I|%sBh0=$7-_u"
    "Bs9im$sL6*a-96_<qTl?ReCS8+NI6*1(u@xsCfR$j>bopqYUq_ZBus8@E`laooCj%{QTMI{D?xcfC%fe(LE>NxhVLbNL=2dd}Cey^3tkQcqd9EI~S&X1VT_`"
    "yM{+pl+k2<n%&XsPi}KCkSgz>@@nC@Q~E=dl3dkw#KfTF3o%uHA$@tl7?fclK<`PUEgjDBL-C+cc&!*n-)D#DFQ`)yw7|mxUBH9{^l1|Sxc(Xs<m!7R#3Z2p"
    "!MQZ`;5qoYaU1BDMwnOphlMLlmBe3rYy`@GXfL#jUEa7$sqUPfBY~^}Ts+bI^9grv(`u$T|59>lx;@oz;i;={?8>Hh>zK~l2*ZEq!nHF9(7hy2jYAwVG!`2("
    "5A^zg#J1z01M3K~`*80BDc}v=aMsDDPKUI47I6~@tiGjVTvV#vbJw;93vrX{k=z>};z`l`cP3~Gy!$YOmIK3G5|At6(9rjJ!vO+e3e42T?Gi&sn*i)eDc-@}"
    "X1E<7Vpz1$BT2l)xhACf+}x`p{kLWN7|7$e+ktCRpT4ItpWuFc(}ahM%4@$gZOZ&wjs&#6Z9~4b?{7u|do6LJ;3<i_ME9`xtE4+Pk_ULKYzX!&AR>&p`2H$e"
    "-UV{fsQ}vb)YBhfk3M^Y>Hsp=pCvY$MXxbwD28fI?@1sHhl$%UGVJQ0*QwyEE1i>e6Kv`4{9Ay=y$AW~j^ThOduTiOhC}hZEbjN_)$}^C@4`St)Pw?o|CZcA"
    "5E6Lo*uq^LDDq(@`T4RQ>6|As3^mR3pn-63DJOmLk?k(#)nZn7#-&0kM4Ji``3s#4sl_E3J3&wXUs#caXrML%;e9rAU@kvNc~U>@i>J7Yux>9XJr1i+w}q40"
    "%$6p!)S)cdne7PI*i}n>u90-vM-qb7qLeg+4_%0c6$rcc!HdCc-AF$E+_UXvWnzVQLltHj^<OPk`?uapXhgBKkLM27{?vQf1uP8=&*fV6d;wn^kM}Ah<5Xg1"
    "*=5Fx&Jgeko~gF>OGa!{JN6-~xMxtTfDlCx3xb}IU?d&l@gg@!y<BeGglus0+SSXim);`w|1)(Rgb-8lUE=7r(c^I!g$bS;FDuJwVxue;nK)GF5#>`d-nysf"
    "(6cVr{?mcc-^#)WcLbkHvbx_KgnidqWV&QCC$cQX9_o!i9Q)Cxg3W}6ZR@)({!n0evi?2yi>vNje}8Al#}3R67(5D2hf1<!`FqRN$mY0ElXMKQKj$96DSu4!"
    "$YG%eghqhq_SAVp=_*$gOL}wk%lM*HW#K?#GXEHMMau;|Tr4{k2o3LEaul`g2`IpGMv{7iatH9cGWD4~TJ4*GD2cGO+q0*IKuljXg}JM6+Gfp4m=}G-qZelR"
    "Bo0HS62k79qEtY;=tJUxnt$1o2wOOsb}l`3Xr>_H+_?5yq5FH%Z{*O*^qyfPl$<^yUPMR*gcQ_<IDY}wmRtyykRq_c4<$q~v;E>rUoaP(9T9-r;tC>AkONM?"
    "^#dm^ob1x(?bL_z0{@tiC)ZME(gVvt4^2BzVfdw9Oo!-j?imyf&}(@dUMyG_;aR6hK~0AYzn5JM!ecDdOo_R;c);O9Ha}*i$963jrbPN=HTnk{Ih(3+%#%L1"
    "@HoShe@*H4hU>I0sq_iB=rk|BQzVo8Zn5#Y`*5%w_<5lV*E*;40OQK9wmFo2LAgvIL40+s2p=%&kqp}yFPlT!^E=VNcQ5kb1CzLEVL}H&TT;cB=5=sv49>o!"
    "lz+`Uz)$`2P_zLy!{Q2;$+3c_r#dL4*Ve_1j}CRL+*qcMH_eGPoF;R*`;*mIVf7&5nA$=<|E$2XAlR>`GSApW{(X2emk5~yUV>j%U{6M`nQAl@^u35!VjQJo"
    "r!tz6EDe>5N&X5+H(EmfZ3@Tu-{rPD(Tx%eyw&j=s-s2hw#cq-44*VmDw%N=si~uaZ36G4I{DN%noSs4ln%7*wS)%%t`M4Z%`b#yv)+&-E3QI?qfQxnK5)vJ"
    "`S?)EpkKy&7)u5$)TCHjiVLAmzUOdkiBleM)WV;XrwW;$n3+3%Mmn<%IhFtzlRe}y$O);D`Sn)o*v%FUq6GZB3Rkj(RbzE<*NES-Jjo!<l7T0rb?0}Jb!!sk"
    "y4*E&K9T8(1Mrv0NpS0iqin3z-Bsdaw2&lBjmS0RQ`4#Xc_mz;H~dht{Iy7^um)pLP|=igGo`~-$OBj?TY~V?TZpMZoj?>GV89;UnqrMvH8YPRtcq)Y+@N~~"
    "gBm-<hQ=zTS<eZn5W+TmhCkGo44^BQC;2PZ`qt2R2yt8iz#>01<tvkza0t%f27v(qy#0vx=<+3heOLxazcLGW>mu(_MI7p#o0IaJs{x4pSSRcbSd4zKJF6jo"
    "LikZpF*}Eaw?Z{CWLVSZ)R?Tv#c~GE*{v8>qLe*|Ufv4nh}BQ~C8-&8vLIwJh?bVH8D{Hzu{bD5=_P{bd#?Io^=r$@EBvFPKbB_RL?_l!R4pYcjx6fIODJRf"
    "ul)WMk(_fAq}A!&uw?`KM~xKDn02d_uRELLesp)A9Xh+P0FIENU+A@~YP6Cx3^THbe@6E6@L?{(-09k1>IyR}aQaLPuh2Rq0`7M|^-QL^2Xb<i7Q{(auHv1d"
    "JqT|V(IUy9J~TfhQ6(kgZeu%<j}=)~au>w-13xbkD#5e$1XIkEXs3*On9ZX=ZwDgj`yINt|9!`7A7>pduD8X2mT4+`VoRDYqDft7P(A8oxWtXfNK4lG;USE&"
    "8Zr3Wycyl=b<lz%j4w1%=kd=&hkPgz-QRYeM*es+FBZb<VJPv$r<p^~nLwG>EeM(?#MhGm#RGSki)KBgJq+Q{gNk+T6V4=){pc$<fTU~Q%&8EtWwywrNkZ49"
    "uUPDJr|vuGt)0|uARo*AsMJDm-DEHaQLZ|^ut01lX1?0Kq;=h>SG15H@VNXit-By9)+qLZx?EK`SsG=SLlkWrtH<v?iRZXJ(_oCxgYSem?2Wdi@h5=_fyHBi"
    "P$Fa$n5|WeiS&w6xw_Tc*z<DIxv5>jy=?PyJb*w^+ddaqY7vWbTux^wEhErPLByoYvk2Z$!zB&R*>}u|-i#j)tApQ<m_EIuLkz$ua&Ex6{yzVd)VdpBR=vmT"
    "k?h2k`v+{<BZt>w8SQ?Lfagw<Oo3ZSa1}xC{?H5@0JVzZ3eHn<ay#Z_j8|W5SP`oIAGSdx;URo((OlYbP!+3`Wn%{5(gp^L7;vy)5cze54#6X=AyGVus!>*V"
    "f^!syoCC{dlum%NOY(&0l`h@DBm}Qo*w!=i7%-{%h+QJqQgyc~31ay+wL<Bae5;ikd~|`U1@u`#f5`Cg>FM3=uil|En2kBv3L<|ol2xP5pPZk_5nzevpU~Sf"
    "MJs#IzXA^N)L64vDF@F+H^g8e9xFXJ3?aCUA)J#^451rObiDlA-<W{j+_NtqdKFk8C3FLqL*3ERyU#b1AlL#3!7HVzKUK2Uv+~wJ)jj&~muS4@7>9tgAL`$)"
    "F7@Z1!SLUMc!BYP;82e_+a28y-=*)h3{z{#*eRmRaMeK~yX)rB_#u6QtOP?j=hQVI|9A$T42V7chB4z~h;^|0l~Tp9=??>@DTzcr93=PAO$!-3--GlmsH%~S"
    "`Y~QLpV=^wG;ucZ(}Bma?3oAob^2b#{dirkes$~O@(U9?az2V72onOyE_J!Jm?rEh_O!VXFrq;<zh3sVxXZn04~YLn&<<udV>U|e*?O*4)l$K|4=ja+;R2d`"
    "Rtf6M+wC2(yE0_#w;KGw2a5Qk?ppL|$J1P8lRn!bMYhJxRj8%7_*PF-7bwzYHS={E01ZSIR=uJauU;1iTVs4_!#q1G46@M-6X}?QskgLQ^9J7FpuQ4KCH?9%"
    "Cy~B85`UidbZhhGbV3#JUEKbE&br+H@H&Y-#0EW*OfN8QkK)~QmT~5obI!}@_wcFWsNQ_a$fyzACHDa29_r(l4U*k4dri_U@a_gS6X%L8@^FRN94p7f5*|cc"
    "Jg>an{m8=wp;w6Bv%6r!LJEln-LgplTu05-v9YbuS6CVFfndVPGKGjhmJde=KA73iHw4VlrIc4Vh%vOo8%_<G-jvG90p?Mn#2|{XD}N^k%O0|;GLZ}L=L!)i"
    "z~mY$h63B~CFtt5XA+$utXx3a5J0MsB>P<@XmMqU-!ZdN>wuu@0}52z^h?3xj@lFw%%f%sDKxwAbhLFv2`&oZ4xAF_S(2}i;sft98mrau7asw_+^Y}AuzHa`"
    "0y-8+S@bU_7cBt#!fvP2p?Kzag`p|dj3)LDDr}&oAq=1p4s61{20(FRyEF9?XG8>){YI}tyqD$0w5bFEC(sAPEw!-Dn`Kv@^>p<h4YCTGZGiyw9LZPchoK(t"
    "H#+tzr!6k2s21x}&bGkElx~2Fzk!!mA7;p}s<4};Ds~9433D1A&X;wcjmp_muoh7#fy)SKQ{9JbOYOFncVq<kTD-<NUcx5J{Y6AM6#=as$cwH{+rNyWQ}hhl"
    "i8$D20cxOmGHSR<c-G99Fj0|^S%^bD#qX9_+3k{b&ZL25P+_Bd@n8C04G7p8>Hjd#VbXos@VK{)qTP?k&fN-k&$-lsti13x`!O?bmH2VLUiWvS5y*$YvG`2V"
    "AsM2feTeQ=&?F|+N3dcR{`!r-)wPBiqhPcY#V3MKNeCJCD%KgP<HUL@bw6|`cfD|u&qDQR4B$P959}tG*u02@lPG4rSoVC*&4MyTdH}2>BF*E=fC}gT7}OnO"
    "qR}OH@~%Zx7WYzb`&s9a`z4GX_2se%KikDUAyF|nIetcQYDfxxja?2?zXHuIjd(qbbgPGw|0yNzshT~NgItLDFCd43M*K2jcfMTyNM8Yum+nLS_Q{ByRD<4b"
    "MlK0iNLXlzE(y^EDf^Xs4d}gzz(6LaMxhxW$l3dKydWyr7-q*CcQ#3Xp=^zA6P(`l?a9Rn-p`)60Mf8oyTa+E;ITee`s{QG0GG{FJ3^v{0W_(#@u+V5%;5KV"
    "QsPuokJMP2H84j^x%c?;$WHtG<n}aX*+SWybnZGFWJy9sL0CUG@96~y!n*+suUI)_I#5lgB7Lh4<|T~s{z$yTU?1`*>81RkcuT|hU(PFmJE6^zDfL3tMdo%E"
    "qP4M?#mhZsWI1#vYm#naPWbe|B<2NfkVUS+c4W)UTW8)=1mqFn$l)QgC?r^l;kk$(icjAenC~oIqW<notB0_W^C1W&ms1y$b7!4^G>GE-aXw`qUZkaH0x&XU"
    "+}M2UJRqJ*-f@ZtDMLqNk1>MNP9u|913nFM3JgLy-@O@*6}KU|NFV0+83}fcs8CttP$4QKA$ap_lIkDkVSBS;Gkn;+zsd6BCF9Za_S_R{`QP_hzwOxbPb$Rq"
    "=)q(DWLIA4*{SUp$OoHn>!<Qk7{)_9c}gVxT^!es2@JQXqZf<k%{9P1bcdXED$^VDyRvje928970)19@RfWNx;4EwwAeHzkW-jaM4ID{-Ws^rCjae%TDzV6?"
    "3Bv8P9DEc6i>0CX%|@8lVxM-Q{CknKMsy7Lb`l;Nx}@+hNLz{y<F>($w<b`5Y_1hS!#Hlwh(<=1ISK}AR|`Ozk#QpdH7{oZKtBXZAoJt%PBLKtGNB~mRIbjk"
    "HuW!lOnO(^R|r2Hl*psdBHmKt2c*sbfG1pg;D~!3ujr$v<A7W+fKU<o_seOJJXEY(Xru-0bSg>(IRhh^M_4fw+fXy6r}QEOY67QKm3n(@_f^gH`xaK6eJx<B"
    "h=)+b(RoZ0;wHSsL%+<H-Oom1e4x!M)+ZXaquhqt)x63F)HA#{lHhB2?C0O;EPIyaYgSCb4Qdt!5#Jt?O(T>OszBnQckE#%W#9c$7WsE#CP@tN(=N$pnmW+-"
    "j)=_^>d^){1YlK*HW=1VQ>-uWL;n=K;b<4OGvpD-xl7UEFdAmKfiwqR+0bM(Txa_oO@dze8s}}d9%W|YBFt&E?Z9_Ev`yYT%($+uQf<c@^fceLjh99iAV0^D"
    "er{s4kjAb%b38Ew)AkzBEn!f1XZ%)2fS=zrz%oM!<Rt22arIikT<-hgF^E{gA}j&~h@fUdhTK_-E9@K7Lmv+yoj|#}iPqI+C^lRReTlfDd1>@C#rqM!`5ol>"
    "IW&2fJfY#e26inEV4r{F4IN$82dKiKt~=Be#+hw*(6&+2Rk=Xuzc9Rn9c>>EJKGMo1W6^~(Hv~;tcQ|*!5xvX0CX(j_6RZg7a6+MjG>|DcY-F^rp=I7p{y6H"
    "Fqi26OnpXim)M}38ZW(j))*bFzQ|1?nDA}B^ixJE6tb%rCsCHkSqMvZ6hGKOwOre|s)cj1AtnnXMwt3HfvY7A{d_{D5;N9hm6g@{@IhzLpL@tmJO4C9FBD30"
    "wn!8JWYor6ipyaKwysZmrFfO&tWyLrrvsZjI5q!2)i!qqT3CvUBu|-RFe2&e^;>z|o2R<^qU3`;B`GO~Y85Ah9jY<1>L#7Mp+zg^8>T03N3>#GCQADuXDEW_"
    "DX<;Dk&^Zl<3DQ?@)P5W+~)&g0GQ`OXU9qN(oR5QZPLLVsvgH1Sr};qFUt99<b_}+J(S8bkPYWhTFLfAQ$xL`oFZN4tJA)y4tRbUOC-cpkyjQLSx1VdK%EBG"
    "p>lXO{Lf=XLxkh6-VsnOmybj|SX4x4cia4AmwEN*ZxUm?7k5HXIg0Y%hs!fIGAq(D7QRWL^10%Z&8ES(3XdGk5B?@<Jnp!Bz3~h(`w;ye=_iyYt8NYM6f5Df"
    "nR#KeU-c<sREli6|0ZoJ0Ew+n<>H1T0GyaZT&N@ctez!b6T+>ExZj{`a+Wbs!c8bd&z^otwYphT_zTuER15)jx%0;wIE}qpLp4&3$mGZszkYl-tu!!H(+*Dk"
    "QOO70ZSE}~ps8OC&*nm)34k9=uw?k$sHR3M^G9vY?(!T4NV@>zJGw?I1BtM2HNBV$SF@u|*b3#2@+gK;-L5`?x1pl0hh&Ox-CO<kn;Lq(e<o7qLjoxELy78)"
    "YS0g)tnV8<hCiv|0AFXH%n$e4!A?yvBcO4f%;!A7qZ$|g%oTlPe3m_yv&iFV-6I|*EGJ!Va6wkeeXJ7YH9y4!zeN`>KA=ky?MCGQei9~504N<dZl`C-DpL??"
    "T$u@9ThKKRvFLAyy%mZEgRp_cUP?ne$r(HnO`~zC<I)B^G~^_gnhn>ZW@I#-pr57Yb-g)A@_Mwx4jYVp#c8jE^^Y~NxjI}>w=J2(G%zwy#(axLb=wjZG_U#*"
    "+$E{6qS~?sauHNGDT2^xSa<$+($-+8D?9eze^fk%C|M8@kRfl0kZbIso>yK-?{YUmKAs{i+4!=%!{df_xqXxsm0J?Q-en+kJ+C1Avyd*8+I!?RmRfMN3{~q1"
    "q$yi6k9-uAl&H+uN-D4S&`Dzdk^k``jiGn_`mpO=;(wNB;zZ4Sa5Ahu%;*NIJF-J<hwXz84FnT0l*IRxiM}#EDpHqH*zDqwN_VmCMRyL7^LBJ;N(EK`%im*("
    "aD^*^!x?iQ`H<AQVS$^(-e5hrOKUP}@a-}`b%W@eS>3J_>+NeEBV$(c9#MYpma<R)XZ|DED%UYef&3-{K59FJlMrs4_X76}akS8yezD+hpMN4)G=jyf5jsQb"
    "QXJW--nd2n<91YfHmpZKHPD|_3+fI0p2Cpykpj2VRq&ppp@ycBX|BQ9+Mk`<QRB&D4Hp8h$-VVz1gns64J{nqMmT`UO+MUNKDg<>25!oXVxF-m3jv?`VTRNK"
    "Q{8FkV6S5^!x{`)d)8ST1Q9C(;sP_~swX5kC1>@hulPxfzdvI0Eqsj*zc~yAH4yywYPu($mF$<XqB^hN6i4($nWRI~_Ka<*-We&=deecv+Mdp<hJqq%#DG0Y"
    "!GjaS2_aB3h@cv9z(NADspjXcWEc<bAhcX`3uk<?Xg)4vUO#OJnWb&N&hLjC-&j9OU~Ot$wA)%b`i6+CO(-2im+mHN*5`?K9fAIpy4H`(*oUTj9RXENioP|6"
    "l@>$gI-6JWMaID}#n!E&`9sMW5O>HPma_AGIDy6GU$N>-U)ECEJl7vWnE1*=ZXvGix|BDEhHzKx(hG9Lx(jRm-5d`dO`#2mJ~+%AcqgUn>prp)ei`5Rw6h*F"
    "-l*pI3RSGPbd*XtF>R>B%cj!@3o6g>^$%!UAn(Kyk#P#{be-xYPE^i(e;pu$$ct9wl+e#yxtC|)P&j{mK{FQ#DE+qiCzw?T2C%giUjwVU47Sfs6jBn0a61I0"
    "#_ZDCv7_ihObwH*&m$yb>vasW!_l8biLrVmTQK3f`GX=P>^Vs6k72@_jT3ni_S7)|FB~FMznw@H{lgSw>^W68Dp~yQ^d5O)EQzO<T7YF<idvyfJls(4sAznk"
    "^MYZn1<~(skF@I@3ycUPmK#^#PycO`CbtHfc@5$CSsjqkwvsTnozQyLH}b=?#_Kbim-6IuJYCPdF`*L_?qK<k`$Wn<G^Jh!y4gVClMl)60%CaQox=^~Z(C!r"
    "xzmi<Q~RQJt$7tOimIeOSE(aIr~%WV5rX6Cu7q5u2gc!z-i(Qyp`-S26h0P^VxrB~I!x<PD!s`AALk=3SdHzqik^b&^(MjXFJJpJ@d~w&FIclIlY?9oLn|S_"
    "VJ-^)2E(ANS-iFHDmFbMrw?Vp^B0)hh~GJ;447Hah;OOuc0WLQ_?`z9H_3+pGYzcpPVvyB*p$Ee%UHX=D{}PCx4o`C(l!&OKg$?S{Kth)$Y;8#e&Nc(ov4-S"
    "4Jv6>^9TJ<*}F!QfGQkyr4mx5I1dWiFnoO`Bg7JnUw!$?DS`oLrgdVU9!nfq?cPGMoc-go`nGWg36)v%Vx?iYn*}+Vhx>;T+nksH00000D<`1HWHy*M00GTr"
    "`{)AzCm8CbvBYQl0ssI200dcD"
)
MODEL_REPAIR_DELTA_RAW_BYTES: Final = 62_587
MODEL_REPAIR_DELTA_RAW_SHA256: Final = (
    "2771e8fee2b432524bcdcb071ad578b4f5ab32c9ddd795c4a57061c39610568a"
)


class OperationModelV2ValidationError(RuntimeError):
    """An installed-byte, lineage, or semantic invariant failed."""


def _fail(message: str) -> None:
    raise OperationModelV2ValidationError(message)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_tree(value: Any, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        _fail("JSON depth cap exceeded")
    if isinstance(value, float):
        _fail("floating JSON literal forbidden")
    if type(value) in (bool, int) or value is None:
        if type(value) is int and value.bit_length() > 65_536:
            _fail("JSON integer cap exceeded")
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            _fail("non-NFC JSON string")
        return
    if type(value) is list:
        for item in value:
            _strict_tree(item, depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or unicodedata.normalize("NFC", key) != key:
                _fail("invalid JSON key")
            _strict_tree(item, depth + 1)
        return
    _fail(f"forbidden JSON type: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _strict_tree(value)
    return (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode("ascii")


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if type(key) is not str or key in result:
            _fail("duplicate or invalid JSON key")
        result[key] = value
    return result


def parse_canonical_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("ascii"),
            object_pairs_hook=_reject_duplicates,
            parse_float=lambda token: (_ for _ in ()).throw(
                OperationModelV2ValidationError(f"{label}: float {token} forbidden")
            ),
            parse_constant=lambda token: (_ for _ in ()).throw(
                OperationModelV2ValidationError(f"{label}: constant {token} forbidden")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OperationModelV2ValidationError(f"{label}: invalid canonical ASCII JSON") from error
    if type(value) is not dict or canonical_bytes(value) != raw:
        _fail(f"{label}: noncanonical JSON")
    return value


def read_immutable(path: Path, *, label: str) -> bytes:
    """Read one immutable file and reject inode/path/parent races."""

    absolute = Path(os.path.abspath(os.fspath(path)))
    parent_path = absolute.parent
    parent_fd = os.open(
        parent_path,
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0),
    )
    descriptor = -1
    try:
        parent_before = os.fstat(parent_fd)
        descriptor = os.open(
            absolute.name,
            os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o444
            or before.st_size < 2
            or before.st_size > MAX_JSON_BYTES
        ):
            _fail(f"{label}: immutable regular single-link 0444 file required")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1 << 20, remaining))
            if not chunk:
                _fail(f"{label}: short read")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            _fail(f"{label}: file grew during read")
        after = os.fstat(descriptor)
        identity = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_nlink,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        if identity != (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_nlink,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            _fail(f"{label}: descriptor identity changed during read")
        live = os.stat(absolute.name, dir_fd=parent_fd, follow_symlinks=False)
        if (live.st_dev, live.st_ino) != (after.st_dev, after.st_ino):
            _fail(f"{label}: installed path changed during read")
        parent_after = os.stat(parent_path, follow_symlinks=False)
        if (
            parent_before.st_dev,
            parent_before.st_ino,
        ) != (
            parent_after.st_dev,
            parent_after.st_ino,
        ):
            _fail(f"{label}: parent path identity changed during read")
        return b"".join(chunks)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent_fd)


def precommit_claims() -> dict[str, bool]:
    return {
        "B06_cleared": False,
        "B06_structural_remedy_prepared": False,
        "backend_independence_claimed": False,
        "complete_C1": False,
        "external_predecessor_commitment_present": False,
        "numerical_execution_performed": False,
        "numerical_implementation_present": False,
        "ordered_roles_8_10_replay_executed": False,
        "production_same_member_bridge_accepted": False,
        "release_eligible": False,
        "role10_numerical_source_materialized": False,
        "same_member_acceptance": False,
        "science_executed": False,
        "submission_eligible": False,
    }


def promotion_claims() -> dict[str, bool]:
    return {
        "B06_cleared": False,
        "B06_structural_remedy_prepared": False,
        "backend_independence_claimed": False,
        "complete_C1": False,
        "ordered_roles_8_10_replay_executed": False,
        "production_same_member_bridge_accepted": False,
        "release_eligible": False,
        "same_member_acceptance": False,
        "submission_eligible": False,
    }


def lifecycle_observations(stage: str) -> dict[str, bool]:
    if stage not in {"source_and_rows", "semantic_receipt", "outer_receipt"}:
        _fail(f"unknown lifecycle stage: {stage}")
    return {
        "external_predecessor_commitment_authenticated": True,
        "numerical_execution_completed": True,
        "numerical_implementation_authenticated": True,
        "outer_validation_completed": stage == "outer_receipt",
        "role10_numerical_source_materialized": True,
        "science_computation_executed": True,
        "this_clean_child_validation_completed": stage == "semantic_receipt",
        "two_clean_child_match_completed": stage == "outer_receipt",
    }


def _decode_delta_node(node: Any, path: str = "$delta") -> None:
    """Reject malformed or ambiguous embedded patch programs."""

    if type(node) is not dict or type(node.get("o")) is not str:
        _fail(f"{path}: malformed delta node")
    operation = node["o"]
    if operation == "r":
        if set(node) != {"o", "v"}:
            _fail(f"{path}: malformed replacement")
        _strict_tree(node["v"])
        return
    if operation == "d":
        if set(node) != {"c", "o", "r"}:
            _fail(f"{path}: malformed dict delta")
        if (
            type(node["r"]) is not list
            or any(type(key) is not str for key in node["r"])
            or len(set(node["r"])) != len(node["r"])
            or type(node["c"]) is not dict
        ):
            _fail(f"{path}: malformed dict delta members")
        for key, child in node["c"].items():
            _decode_delta_node(child, f"{path}/{key}")
        return
    if operation == "l":
        if set(node) != {"c", "n", "o"}:
            _fail(f"{path}: malformed list delta")
        if type(node["n"]) is not int or node["n"] < 0 or type(node["c"]) is not dict:
            _fail(f"{path}: malformed list delta members")
        seen: set[int] = set()
        for token, child in node["c"].items():
            if (
                not token.isascii()
                or not token.isdecimal()
                or (token != "0" and token.startswith("0"))
            ):
                _fail(f"{path}: noncanonical list index")
            index = int(token)
            if index >= node["n"] or index in seen:
                _fail(f"{path}: invalid list index")
            seen.add(index)
            _decode_delta_node(child, f"{path}/{token}")
        return
    _fail(f"{path}: unknown delta operation")


def _decode_embedded_delta(
    encoded: str, raw_bytes: int, raw_sha256: str, label: str
) -> dict[str, Any]:
    try:
        compressed = base64.b85decode(encoded.encode("ascii"))
        raw = lzma.decompress(compressed)
        if len(raw) != raw_bytes or sha256(raw) != raw_sha256:
            _fail(f"embedded {label} delta length/SHA-256 mismatch")
        delta = json.loads(raw.decode("ascii"), object_pairs_hook=_reject_duplicates)
    except (ValueError, lzma.LZMAError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise OperationModelV2ValidationError(
            f"embedded {label} semantic delta is corrupt"
        ) from error
    if type(delta) is not dict:
        _fail(f"embedded {label} semantic delta has non-object root")
    _decode_delta_node(delta, f"${label}_delta")
    return delta


@lru_cache(maxsize=1)
def decoded_delta() -> dict[str, Any]:
    return _decode_embedded_delta(
        MODEL_DELTA_B85,
        MODEL_DELTA_RAW_BYTES,
        MODEL_DELTA_RAW_SHA256,
        "base",
    )


@lru_cache(maxsize=1)
def decoded_repair_delta() -> dict[str, Any] | None:
    if not MODEL_REPAIR_DELTA_B85:
        return None
    return _decode_embedded_delta(
        MODEL_REPAIR_DELTA_B85,
        MODEL_REPAIR_DELTA_RAW_BYTES,
        MODEL_REPAIR_DELTA_RAW_SHA256,
        "repair",
    )


def _apply_delta(value: Any, node: dict[str, Any], path: str = "$") -> Any:
    operation = node["o"]
    if operation == "r":
        return copy.deepcopy(node["v"])
    if operation == "d":
        if type(value) is not dict:
            _fail(f"{path}: delta expected object")
        result = copy.deepcopy(value)
        for key in node["r"]:
            if key not in result:
                _fail(f"{path}: delta removal missing key {key!r}")
            del result[key]
        for key, child in node["c"].items():
            if child["o"] != "r" and key not in result:
                _fail(f"{path}: delta update missing key {key!r}")
            result[key] = _apply_delta(result.get(key), child, f"{path}/{key}")
        return result
    if operation == "l":
        if type(value) is not list or len(value) != node["n"]:
            _fail(f"{path}: delta list cardinality mismatch")
        result = copy.deepcopy(value)
        for token, child in node["c"].items():
            index = int(token)
            result[index] = _apply_delta(result[index], child, f"{path}/{token}")
        return result
    _fail(f"{path}: unhandled delta operation")


@lru_cache(maxsize=1)
def _v1_model_cached() -> dict[str, Any]:
    raw = read_immutable(V1_PATH, label="frozen v1 lineage")
    if sha256(raw) != V1_SHA256:
        _fail("frozen v1 lineage SHA-256 mismatch")
    v1 = parse_canonical_json(raw, "frozen v1 lineage")
    if v1.get("schema") != V1_SCHEMA:
        _fail("frozen v1 lineage schema mismatch")
    return v1


@lru_cache(maxsize=1)
def _expected_model_cached() -> dict[str, Any]:
    """Reconstruct every v2 subtree from authenticated v1 plus source delta."""

    expected = _apply_delta(_v1_model_cached(), decoded_delta())
    repair = decoded_repair_delta()
    if repair is not None:
        expected = _apply_delta(expected, repair)
    if type(expected) is not dict:
        _fail("reconstructed v2 root is not an object")
    return expected


def expected_model() -> dict[str, Any]:
    """Return a defensive copy of the independently reconstructed oracle."""

    return copy.deepcopy(_expected_model_cached())


def _json_pointer(root: dict[str, Any], pointer: str) -> Any:
    if not pointer.startswith("/"):
        _fail(f"invalid JSON pointer: {pointer!r}")
    value: Any = root
    for raw_token in pointer[1:].split("/"):
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if type(value) is dict and token in value:
            value = value[token]
        elif type(value) is list and token.isdecimal() and int(token) < len(value):
            value = value[int(token)]
        else:
            _fail(f"unresolved JSON pointer: {pointer}")
    return value


def _walk(value: Any, path: str = "$") -> Any:
    if type(value) is dict:
        for key, child in value.items():
            yield from _walk(child, f"{path}/{key}")
    elif type(value) is list:
        for index, child in enumerate(value):
            yield from _walk(child, f"{path}/{index}")
    else:
        yield path, value


def _first_difference(actual: Any, expected: Any, path: str = "$") -> str | None:
    if type(actual) is not type(expected):
        return f"{path}: type {type(actual).__name__} != {type(expected).__name__}"
    if type(actual) is dict:
        actual_keys = set(actual)
        expected_keys = set(expected)
        if actual_keys != expected_keys:
            return (
                f"{path}: object keys differ; "
                f"missing={sorted(expected_keys - actual_keys)!r} "
                f"extra={sorted(actual_keys - expected_keys)!r}"
            )
        for key in expected:
            difference = _first_difference(actual[key], expected[key], f"{path}/{key}")
            if difference is not None:
                return difference
        return None
    if type(actual) is list:
        if len(actual) != len(expected):
            return f"{path}: list cardinality {len(actual)} != {len(expected)}"
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            difference = _first_difference(actual_item, expected_item, f"{path}/{index}")
            if difference is not None:
                return difference
        return None
    if actual != expected:
        return f"{path}: value differs"
    return None


def _targeted_semantic_joins(model: dict[str, Any]) -> None:
    if model.get("schema") != MODEL_SCHEMA or model.get("status") != MODEL_STATUS:
        _fail("root schema/status mismatch")
    if model.get("claim_boundary") != precommit_claims():
        _fail("precommit claim boundary is not the exact all-false map")

    v1 = _v1_model_cached()
    for section in (
        "authority_bindings",
        "authority_model",
        "method_contract",
        "resource_caps",
    ):
        if model.get(section) != v1.get(section):
            _fail(f"declared v1 reuse differs at {section}")
    artifact = model.get("artifact_contract")
    v1_artifact = v1.get("artifact_contract")
    if type(artifact) is not dict or type(v1_artifact) is not dict:
        _fail("artifact contract missing during v1 reuse check")
    for section in (
        "directory_paths",
        "file_paths",
        "path_templates",
        "top_file_inventory",
        "totals",
    ):
        if artifact.get(section) != v1_artifact.get(section):
            _fail(f"declared v1 artifact reuse differs at {section}")
    rows_for_reuse = artifact.get("rows")
    v1_rows = v1_artifact.get("rows")
    if (
        type(rows_for_reuse) is not list
        or type(v1_rows) is not list
        or len(rows_for_reuse) != len(v1_rows)
    ):
        _fail("declared v1 row reuse cardinality mismatch")
    for index, (row, v1_row) in enumerate(zip(rows_for_reuse, v1_rows, strict=True)):
        if type(row) is not dict or type(v1_row) is not dict:
            _fail(f"row {index} is not an object")
        if row.get("row_schema") != ROW_SCHEMA:
            _fail(f"row {index} v1-to-v2 schema transform mismatch")
        if v1_row.get("row_schema") != ("encounter_c1_n0_killing_factor_geometry_row_v1"):
            _fail(f"row {index} v1 source schema mismatch")
        if {key: value for key, value in row.items() if key != "row_schema"} != {
            key: value for key, value in v1_row.items() if key != "row_schema"
        }:
            _fail(f"row {index} differs beyond declared row-schema transform")

    wire = model.get("wire_schema_contract")
    if type(wire) is not dict:
        _fail("wire schema contract missing")
    lifecycle_maps = wire.get("lifecycle_maps")
    if type(lifecycle_maps) is not dict:
        _fail("lifecycle maps missing")
    for stage in ("source_and_rows", "semantic_receipt", "outer_receipt"):
        if lifecycle_maps.get(stage) != lifecycle_observations(stage):
            _fail(f"{stage} lifecycle map mismatch")
    if lifecycle_maps.get("promotion_claims") != promotion_claims():
        _fail("promotion lifecycle claims are not the exact all-false map")

    pointer_prefixes = (
        "/wire_schema_contract/",
        "/replay_plan_contract/",
        "/publication_contract/",
        "/process_contract/",
    )
    pointer_values = [
        value
        for _, value in _walk(model)
        if type(value) is str and value.startswith(pointer_prefixes)
    ]
    if len(pointer_values) != 99 or len(set(pointer_values)) != 49:
        _fail(
            "normative internal pointer catalog mismatch: "
            f"expected 99 occurrences/49 unique, got "
            f"{len(pointer_values)}/{len(set(pointer_values))}"
        )
    for pointer in pointer_values:
        _json_pointer(model, pointer)

    totals = model.get("artifact_contract", {}).get("totals")
    if totals != {
        "configuration_rows": 12,
        "contact_interval_bytes": 3_730_224,
        "contact_interval_records": 233_139,
        "directories": 14,
        "files": 73,
        "profile_files": 48,
        "profile_interval_bytes": 109_632,
        "profile_interval_records": 6_852,
        "raw_numerical_leaves": 60,
        "row_manifests": 12,
        "top_manifests": 1,
    }:
        _fail("artifact topology/count totals mismatch")
    rows = model.get("artifact_contract", {}).get("rows")
    if (
        type(rows) is not list
        or len(rows) != 12
        or any(type(row) is not dict or row.get("row_schema") != ROW_SCHEMA for row in rows)
    ):
        _fail("row cardinality/order/schema mismatch")

    contact_counts = (
        model.get("classification_contract", {}).get("contact", {}).get("global_counts")
    )
    if contact_counts != {
        "full": 4_142,
        "partial": 1_304,
        "total": 233_139,
        "zero": 227_693,
    }:
        _fail("contact classification counts mismatch")
    if sum(contact_counts[key] for key in ("zero", "full", "partial")) != 233_139:
        _fail("contact classification partition does not close")
    profile_ledger = (
        model.get("classification_contract", {}).get("profile", {}).get("per_row_profile_ledger")
    )
    if type(profile_ledger) is not dict or profile_ledger.get("cardinality") != 48:
        _fail("profile ledger cardinality mismatch")

    replay = model.get("replay_plan_contract")
    if (
        type(replay) is not dict
        or replay.get("schema") != PLAN_SCHEMA
        or replay.get("status") != PLAN_STATUS
    ):
        _fail("replay-plan v2 schema/status mismatch")
    slots = replay.get("slot_templates")
    expected_slot_ids = [
        "role8_request",
        "role8_artifact",
        "role8_validation_receipt",
        "role9_request",
        "role9_artifact",
        "role9_validation_receipt",
        "role10_request",
        "role10_artifact_directory",
        "role10_semantic_receipt",
        "role10_outer_validation_receipt",
    ]
    if (
        type(slots) is not list
        or [slot.get("slot_id") for slot in slots if type(slot) is dict] != expected_slot_ids
        or [slot.get("ordinal") for slot in slots if type(slot) is dict] != list(range(10))
    ):
        _fail("ten-slot replay-plan topology/order mismatch")
    plan_claims = replay.get("plan_claim_boundary")
    if type(plan_claims) is not dict or any(plan_claims.values()):
        _fail("replay-plan precommit claims must all be false")

    runtime = replay.get("runtime_closure")
    expected_runtime_keys = [
        "claim_boundary",
        "global_runner",
        "host_runtime_trust_boundary",
        "process_contract",
        "roles",
        "schema",
        "status",
    ]
    if (
        type(runtime) is not dict
        or runtime.get("schema") != RUNTIME_SCHEMA
        or runtime.get("exact_keys") != expected_runtime_keys
    ):
        _fail("runtime-closure v1 catalog mismatch")
    runtime_claims = runtime.get("claim_boundary")
    if (
        type(runtime_claims) is not dict
        or runtime_claims.get("complete_host_runtime_image") is not False
        or runtime_claims.get("host_runtime_dependencies_byte_pinned") is not False
        or runtime_claims.get("complete_report_local_and_declared_numerical_runtime_closure")
        is not True
    ):
        _fail("runtime-closure host trust-boundary claim mismatch")
    runtime_fields = runtime.get("field_schemas")
    if (
        type(runtime_fields) is not dict
        or runtime_fields.get("global_runner")
        != {"object_schema": "/replay_plan_contract/objects/runtime_global_runner"}
        or runtime_fields.get("host_runtime_trust_boundary")
        != {"object_schema": "/replay_plan_contract/objects/runtime_host_trust_boundary"}
    ):
        _fail("runtime-closure runner/host schema join mismatch")

    replay_objects = replay.get("objects")
    if type(replay_objects) is not dict:
        _fail("replay-plan object-schema catalog mismatch")
    resolved_dependency = replay_objects.get("resolved_python_dependency")
    if (
        type(resolved_dependency) is not dict
        or resolved_dependency.get("exact_keys") != ["import_name", "origin_kind", "path", "sha256"]
        or not any(
            type(rule) is str and "file_runtime_prefix" in rule
            for rule in resolved_dependency.get("classification_rules", [])
        )
    ):
        _fail("resolved Python dependency schema mismatch")
    runtime_runner = replay_objects.get("runtime_global_runner")
    if (
        type(runtime_runner) is not dict
        or runtime_runner.get("exact_keys")
        != [
            "code_input",
            "python_executable",
            "python_imports",
            "python_runtime",
            "report_local_dependencies",
            "resolved_python_dependencies",
            "runner_contract_sha256",
            "runner_id",
        ]
        or runtime_runner.get("field_schemas", {})
        .get("resolved_python_dependencies", {})
        .get("array_item_schema")
        != "/replay_plan_contract/objects/resolved_python_dependency"
    ):
        _fail("global-runner runtime schema mismatch")
    host_boundary = replay_objects.get("runtime_host_trust_boundary")
    if (
        type(host_boundary) is not dict
        or host_boundary.get("exact_keys")
        != [
            "byte_complete",
            "darwin_kernel_release",
            "machine",
            "macos_build_version",
            "scope",
            "status",
        ]
        or host_boundary.get("field_schemas", {}).get("byte_complete") != "literal_false"
    ):
        _fail("explicit non-byte-complete host runtime schema mismatch")

    runner = replay.get("global_replay_runner_contract")
    if (
        type(runner) is not dict
        or runner.get("runner_id") != "roles_8_10_global_replay_runner_v2"
        or runner.get("entrypoint_basename") != "execute_continuum_c1_n0_roles_8_10_replay_v2.py"
        or "runner_contract_sha256" not in runner.get("runtime_binding", "")
        or "seven_materialized_output_slots_absent" not in runner.get("seven_output_preflight", "")
    ):
        _fail("global replay runner v2 contract mismatch")

    request_contract = replay.get("request_contract")
    expected_cross_request_join = (
        "all_three_requests_have_byte_identical_external_predecessor_commitment_pin_"
        "plan_pin_shared_precommit_context_sha256_and_shared_replay_context_sha256_values"
    )
    if (
        type(request_contract) is not dict
        or expected_cross_request_join not in request_contract.get("join_rules", [])
        or request_contract.get("shared_replay_preimage", {}).get("exact_keys")
        != [
            "external_predecessor_commitment_sha256",
            "replay_plan_sha256",
            "shared_precommit_context_sha256",
        ]
    ):
        _fail("three-request byte-identity/digest join mismatch")

    lineage = model.get("lineage", {}).get("v1")
    if type(lineage) is not dict or lineage != {
        "path": (
            "artifacts/data/continuum_c1_n0_role10_numerical_operation_model_v1_candidate.json"
        ),
        "schema": V1_SCHEMA,
        "sha256": V1_SHA256,
        "status": "HISTORICAL_RESULT_BLIND_DRAFT_SUPERSEDED_BEFORE_EXTERNAL_COMMITMENT",
    }:
        _fail("v1 lineage binding mismatch")

    lock = model.get("publication_contract", {}).get("single_writer_lock")
    if type(lock) is not dict or "parent" not in lock.get("serialization_scope", ""):
        _fail("parent-global single-writer serialization missing")
    if "independent_of_request_or_target_names" not in lock.get(
        "identity", ""
    ) or "persistent" not in lock.get("identity", ""):
        _fail("parent-global persistent lock identity mismatch")

    environment = model.get("process_contract", {}).get("environment")
    if type(
        environment
    ) is not dict or "^0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+:0x[0-9A-Fa-f]+$" not in environment.get(
        "darwin_observation_exception", ""
    ):
        _fail("Darwin environment observation grammar mismatch")
    argv = model.get("process_contract", {}).get("argv")
    if type(argv) is not dict or set(argv) != {
        "child_semantic_verifier",
        "producer",
        "transaction_orchestrator",
    }:
        _fail("process argv catalog mismatch")
    for name, vector in argv.items():
        if type(vector) is not list or vector[1:3] != ["-I", "-B"]:
            _fail(f"{name} exact isolated argv prefix mismatch")

    process = model.get("process_contract")
    if type(process) is not dict:
        _fail("process contract mismatch")
    observations = process.get("run_observation_contract")
    if (
        type(observations) is not dict
        or observations.get("cardinality") != 3
        or observations.get("order") != ["producer_child", "semantic_child_0", "semantic_child_1"]
        or observations.get("schema") != "/wire_schema_contract/objects/run_observation"
    ):
        _fail("three-run observation contract mismatch")

    acknowledgements = process.get("ack_contracts")
    if type(acknowledgements) is not dict or set(acknowledgements) != {
        "encoding",
        "maximum_bytes",
        "producer_child",
        "public_transaction_commit",
        "semantic_child",
    }:
        _fail("process ACK catalog mismatch")
    producer_ack = acknowledgements.get("producer_child")
    semantic_ack = acknowledgements.get("semantic_child")
    public_ack = acknowledgements.get("public_transaction_commit")
    composite_pointer = "/process_contract/digest_contracts/staged_artifact_binding_sha256"
    if (
        type(producer_ack) is not dict
        or producer_ack.get("exact_keys")
        != [
            "darwin_cf_user_text_encoding_observation",
            "schema",
            "staged_artifact_binding_sha256",
            "status",
        ]
        or producer_ack.get("field_schemas", {}).get("staged_artifact_binding_sha256")
        != composite_pointer
        or type(semantic_ack) is not dict
        or semantic_ack.get("exact_keys")
        != [
            "darwin_cf_user_text_encoding_observation",
            "schema",
            "semantic_receipt_sha256",
            "status",
        ]
        or type(public_ack) is not dict
        or public_ack.get("exact_keys")
        != [
            "artifact_binding_sha256",
            "darwin_cf_user_text_encoding_observation",
            "outer_receipt_sha256",
            "schema",
            "semantic_receipt_sha256",
            "status",
        ]
        or public_ack.get("field_schemas", {}).get("artifact_binding_sha256") != composite_pointer
        or len(public_ack.get("join_rules", [])) != 2
    ):
        _fail("producer/semantic/public ACK contract mismatch")
    staged_digest = process.get("digest_contracts", {}).get("staged_artifact_binding_sha256")
    if (
        type(staged_digest) is not dict
        or staged_digest.get("domain") != "encounter-role10-staged-artifact-ack-binding-v1"
        or "complete_canonical_top_manifest_envelope" not in staged_digest.get("preimage", "")
        or "file_inventory_tree_sha256" not in staged_digest.get("preimage", "")
        or "exactly_72_inventory_entries" not in staged_digest.get("recomputation", "")
    ):
        _fail("whole-artifact composite digest contract mismatch")

    tree_stability = (
        model.get("wire_schema_contract", {}).get("objects", {}).get("tree_stability_evidence")
    )
    if (
        type(tree_stability) is not dict
        or tree_stability.get("types", {}).get("before_children_tree_sha256") != composite_pointer
        or tree_stability.get("types", {}).get("after_child_0_tree_sha256") != composite_pointer
        or tree_stability.get("types", {}).get("after_child_1_tree_sha256") != composite_pointer
        or tree_stability.get("join") != "all_three_tree_sha256_values_are_identical"
    ):
        _fail("tree-stability composite binding mismatch")

    deadline = process.get("deadline_accounting")
    if (
        type(deadline) is not dict
        or deadline.get("absolute_maximum_single_child_wall_seconds") != 1_200
        or deadline.get("semantic_seconds") != 1_140
        or deadline.get("outer_nonchild_reserve_seconds") != 300
        or deadline.get("outer_total_seconds") != 2_700
        or deadline.get("phase_caps_seconds")
        != {
            "producer_including_signal_reap": 1_200,
            "semantic_children_concurrent_including_signal_reap": 1_140,
            "transaction_orchestrator_total": 2_700,
        }
        or 1_200 + 1_140 + 300 > 2_700
        or "two_semantic_children_are_concurrent" not in deadline.get("timing_rule", "")
        or "2640_less_than_or_equal_to_2700"
        not in " ".join(rule for rule in deadline.get("deadline_rules", []) if type(rule) is str)
    ):
        _fail("concurrent semantic deadline accounting mismatch")

    publication = model.get("publication_contract")
    journal = publication.get("recovery_journal") if type(publication) is dict else None
    expected_journal_keys = [
        "auxiliary_semantic_receipts",
        "journal_identity",
        "owned_stage_root",
        "output_parent_identity",
        "prepublication_journal_snapshot_sha256",
        "request_sha256",
        "staged_identity_ledger_sha256",
        "staged_outputs",
        "state",
        "target_slots",
    ]
    expected_states = [
        "INTENT_DURABLE",
        "ABOUT_TO_CREATE_STAGE_ROOT",
        "STAGE_ROOT_IDENTITY_RECORDED",
        "ABOUT_TO_CREATE_ARTIFACT_DIRECTORY",
        "ARTIFACT_DIRECTORY_IDENTITY_RECORDED",
        "ABOUT_TO_CREATE_SEMANTIC_RECEIPT",
        "SEMANTIC_RECEIPT_IDENTITY_RECORDED",
        "ABOUT_TO_CREATE_OUTER_RECEIPT",
        "OUTER_RECEIPT_IDENTITY_RECORDED",
        "ABOUT_TO_CREATE_CHILD_0_RECEIPT",
        "CHILD_0_RECEIPT_IDENTITY_RECORDED",
        "ABOUT_TO_CREATE_CHILD_1_RECEIPT",
        "CHILD_1_RECEIPT_IDENTITY_RECORDED",
        "STAGING_IDENTITIES_COMPLETE",
        "PRODUCER_COMPLETED",
        "SEMANTIC_CHILDREN_MATCHED",
        "ABOUT_TO_REMOVE_CHILD_1_RECEIPT",
        "CHILD_1_RECEIPT_REMOVED",
        "ABOUT_TO_REMOVE_CHILD_0_RECEIPT",
        "CHILD_0_RECEIPT_REMOVED",
        "PREPARED_FOR_INSTALL",
        "ABOUT_TO_INSTALL_ARTIFACT",
        "ARTIFACT_INSTALLED",
        "ABOUT_TO_INSTALL_SEMANTIC_RECEIPT",
        "SEMANTIC_RECEIPT_INSTALLED",
        "ABOUT_TO_INSTALL_OUTER_RECEIPT",
        "OUTER_RECEIPT_INSTALLED",
        "COMMITTED",
    ]
    expected_matrix_keys = {
        "ABOUT_TO_CREATE_ARTIFACT_DIRECTORY",
        "ABOUT_TO_CREATE_CHILD_0_RECEIPT",
        "ABOUT_TO_CREATE_CHILD_1_RECEIPT",
        "ABOUT_TO_CREATE_OUTER_RECEIPT",
        "ABOUT_TO_CREATE_SEMANTIC_RECEIPT",
        "ABOUT_TO_CREATE_STAGE_ROOT",
        "ABOUT_TO_REMOVE_CHILD_0_RECEIPT",
        "ABOUT_TO_REMOVE_CHILD_1_RECEIPT",
        "ARTIFACT_DIRECTORY_IDENTITY_RECORDED",
        "CHILD_0_RECEIPT_IDENTITY_RECORDED",
        "CHILD_0_RECEIPT_REMOVED_through_ABOUT_TO_INSTALL_OUTER_RECEIPT",
        "CHILD_1_RECEIPT_IDENTITY_RECORDED",
        "CHILD_1_RECEIPT_REMOVED",
        "INTENT_DURABLE",
        "OUTER_RECEIPT_IDENTITY_RECORDED",
        "OUTER_RECEIPT_INSTALLED_and_COMMITTED",
        "SEMANTIC_RECEIPT_IDENTITY_RECORDED",
        "STAGE_ROOT_IDENTITY_RECORDED",
        "STAGING_IDENTITIES_COMPLETE_through_SEMANTIC_CHILDREN_MATCHED",
    }
    if (
        type(journal) is not dict
        or journal.get("exact_keys") != expected_journal_keys
        or journal.get("state_order") != expected_states
        or len(set(journal.get("state_order", []))) != 28
        or type(journal.get("state_value_matrix")) is not dict
        or set(journal["state_value_matrix"]) != expected_matrix_keys
        or any(
            type(value) is not str
            or "identit" not in value
            or "prepublication_journal_snapshot" not in value
            for value in journal["state_value_matrix"].values()
        )
    ):
        _fail("28-state journal identity/null-value matrix mismatch")
    journal_fields = journal.get("field_schemas")
    if (
        type(journal_fields) is not dict
        or journal_fields.get("auxiliary_semantic_receipts", {}).get("cardinality") != 2
        or journal_fields.get("staged_outputs", {}).get("cardinality") != 3
        or journal_fields.get("target_slots", {}).get("cardinality") != 3
        or "ABOUT_TO_REMOVE" not in journal.get("identity_location_join", "")
    ):
        _fail("journal six-identity ledger/cardinality mismatch")

    temporary_receipts = model.get("receipt_contract", {}).get("temporary_child_receipts")
    expected_auxiliary_paths = [
        ".semantic-child-0-receipt.json",
        ".semantic-child-1-receipt.json",
    ]
    if (
        type(temporary_receipts) is not dict
        or temporary_receipts.get("cardinality") != 2
        or temporary_receipts.get("paths_in_run_order") != expected_auxiliary_paths
        or any(
            "/" in path or not path.startswith(".") or not path.endswith(".json")
            for path in temporary_receipts.get("paths_in_run_order", [])
            if type(path) is str
        )
    ):
        _fail("direct hidden auxiliary semantic-receipt path mismatch")
    output_parent = publication.get("output_parent")
    expected_parent_checks = [
        "before_preflight",
        "before_each_install",
        "after_each_install_and_parent_fsync",
        "before_caller_commit_ACK",
        "after_rollback",
    ]
    if (
        type(output_parent) is not dict
        or output_parent.get("path_rebind_identity_checks") != expected_parent_checks
        or any(
            "after_caller" in check
            for check in output_parent.get("path_rebind_identity_checks", [])
            if type(check) is str
        )
    ):
        _fail("output-parent caller-ACK identity boundary mismatch")

    future_hashes = model.get("forbidden_surface", {})
    for key in (
        "future_code_hashes",
        "future_output_tree_or_relation_digest_values_in_precommit_model",
        "unknown_future_output_or_result_hash_pins",
    ):
        value = future_hashes.get(key)
        if type(value) is not str or not value:
            _fail(f"future hash prohibition missing: {key}")
    forbidden_keys = {
        "document_sha256",
        "closed_object_schemas",
        "model_section_binding_",
    }
    for path, value in _walk(model):
        if any(
            token in path or (type(value) is str and token in value) for token in forbidden_keys
        ):
            _fail(f"forbidden stale/cyclic reference at {path}")


def validate_value(
    value: dict[str, Any],
    *,
    enforce_frozen_sha: bool = False,
    observed_raw: bytes | None = None,
) -> str:
    """Validate semantic content; optionally authenticate installed bytes."""

    if type(value) is not dict:
        _fail("candidate root must be an object")
    _strict_tree(value)
    _targeted_semantic_joins(value)
    difference = _first_difference(value, _expected_model_cached())
    if difference is not None:
        _fail(f"semantic oracle mismatch: {difference}")
    if enforce_frozen_sha:
        if observed_raw is None:
            _fail("frozen SHA enforcement requires observed canonical bytes")
        if canonical_bytes(value) != observed_raw:
            _fail("observed bytes do not canonically encode supplied value")
        observed_sha = sha256(observed_raw)
        if observed_sha != FROZEN_MODEL_SHA256:
            _fail("frozen v2 whole-file SHA-256 mismatch")
        return observed_sha
    return sha256(canonical_bytes(value))


def validate(path: Path | str = DEFAULT_MODEL, *, enforce_frozen_sha: bool = True) -> str:
    model_path = Path(path)
    raw = read_immutable(model_path, label="role10 operation-model v2")
    value = parse_canonical_json(raw, "role10 operation-model v2")
    return validate_value(value, enforce_frozen_sha=enforce_frozen_sha, observed_raw=raw)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument(
        "--no-frozen-sha",
        action="store_true",
        help="run the complete semantic oracle without the installed-byte hash gate",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        digest = validate(arguments.model, enforce_frozen_sha=not arguments.no_frozen_sha)
    except (OSError, OperationModelV2ValidationError) as error:
        print(f"HOLD_ROLE10_OPERATION_MODEL_V2 {error}")
        return 1
    print(f"PASS_ROLE10_OPERATION_MODEL_V2_SEMANTIC {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
