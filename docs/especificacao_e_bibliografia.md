# Bibliografia: cálculo de idades U-Pb em zircão

Oct 17, 2026 · @Cibele Carolina Montibeller

## Como usar esta bibliografia

O núcleo de cálculo do software sai de cerca de 10 artigos: constantes (Jaffey 1971, Hiess 2012), equações e concórdia (Wetherill 1956, Tera & Wasserburg 1972), regressão (York 2004), idade concórdia (Ludwig 1998), Pb comum (Stacey & Kramers 1975), incertezas e reporte (Horstwood 2016) e o motor de referência IsoplotR (Vermeesch 2018). O resto serve para calibrar, validar e documentar.

Cada item traz o DOI ou link e uma linha sobre o que ele entrega ao cálculo. Ordem de leitura sugerida: uma revisão geral, depois as seções na ordem em que o dado passa pelo software (constantes, equações, Pb comum, estatística, incertezas).

## Revisões gerais do método

Comece por estas duas: juntas cobrem a teoria do sistema U-Th-Pb e as três técnicas analíticas, com as equações básicas.

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Schoene, B. (2014). U–Th–Pb Geochronology. Treatise on Geochemistry, 2ª ed., v. 4, p. 341–378 | [10.1016/B978-0-08-095975-7.00310-7](https://doi.org/10.1016/B978-0-08-095975-7.00310-7) | Revisão mais completa: equações de idade, concórdia, discórdia, Pb comum, desequilíbrio e fontes de incerteza num só texto |
| Schaltegger, U., Schmitt, A.K., Horstwood, M.S.A. (2015). U–Th–Pb zircon geochronology by ID-TIMS, SIMS, and laser ablation ICP-MS: recipes, interpretations, and opportunities. Chemical Geology 402, 89–110 | [10.1016/j.chemgeo.2015.02.028](https://doi.org/10.1016/j.chemgeo.2015.02.028) | Compara as três técnicas e diz como interpretar idades em zircão (herança, perda de Pb, precisão esperada) |

## Constantes de decaimento e razão 238U/235U

O software deve usar λ238 = 1,55125 × 10⁻¹⁰ a⁻¹ e λ235 = 9,8485 × 10⁻¹⁰ a⁻¹ (Jaffey et al. 1971) e 238U/235U = 137,818 (Hiess et al. 2012), deixando o valor antigo 137,88 como opção para reproduzir dados publicados.

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Jaffey, A.H. et al. (1971). Precision measurement of half-lives and specific activities of 235U and 238U. Physical Review C 4, 1889–1906 | [10.1103/PhysRevC.4.1889](https://doi.org/10.1103/PhysRevC.4.1889) | Meias-vidas de 238U e 235U e suas incertezas; base de todas as equações de idade |
| Steiger, R.H., Jäger, E. (1977). Subcommission on geochronology: Convention on the use of decay constants in geo- and cosmochronology. EPSL 36, 359–362 | [10.1016/0012-821X(77)90060-7](<https://doi.org/10.1016/0012-821X(77)90060-7>) | Convenção IUGS das constantes e da razão 238U/235U = 137,88 usada até 2012 |
| Hiess, J., Condon, D.J., McLean, N., Noble, S.R. (2012). 238U/235U systematics in terrestrial uranium-bearing minerals. Science 335, 1610–1614 | [10.1126/science.1215507](https://doi.org/10.1126/science.1215507) | Novo valor 238U/235U = 137,818 ± 0,045 em zircão; entra na idade 207Pb/206Pb e no diagrama Tera-Wasserburg |

## Equações de idade e diagramas concórdia

As três idades aparentes saem destas equações (Pb\* = Pb radiogênico); a 207Pb/206Pb não tem solução analítica e o software precisa resolvê-la por iteração (Newton-Raphson ou bisseção).

```latex
\frac{^{206}\mathrm{Pb}^*}{^{238}\mathrm{U}} = e^{\lambda_{238} t} - 1 \qquad \frac{^{207}\mathrm{Pb}^*}{^{235}\mathrm{U}} = e^{\lambda_{235} t} - 1 \qquad \frac{^{207}\mathrm{Pb}^*}{^{206}\mathrm{Pb}^*} = \frac{1}{137.818}\,\frac{e^{\lambda_{235} t} - 1}{e^{\lambda_{238} t} - 1}
```

No diagrama de Wetherill o eixo x é 207Pb/235U e o y é 206Pb/238U; no de Tera-Wasserburg o x é 238U/206Pb e o y é 207Pb/206Pb, medidos sem correção de Pb comum.

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Wetherill, G.W. (1956). Discordant uranium-lead ages, I. Transactions, American Geophysical Union 37, 320–326 | [10.1029/TR037i003p00320](https://doi.org/10.1029/TR037i003p00320) | Define a curva concórdia 206Pb/238U vs. 207Pb/235U e a interpretação geométrica da discordância |
| Tera, F., Wasserburg, G.J. (1972). U-Th-Pb systematics in three Apollo 14 basalts and the problem of initial Pb in lunar rocks. EPSL 14, 281–304 | [10.1016/0012-821X(72)90128-8](<https://doi.org/10.1016/0012-821X(72)90128-8>) | Diagrama 238U/206Pb vs. 207Pb/206Pb, padrão para LA-ICP-MS e para ancorar Pb comum no eixo y |

## Discórdia, interceptos e regressão

A discórdia é uma reta ajustada com erros em x e y correlacionados; o algoritmo de York (2004) é o que o software deve implementar, e Ludwig (1980, 2000) diz como levar as incertezas até os interceptos superior e inferior.

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| York, D. (1968). Least squares fitting of a straight line with correlated errors. EPSL 5, 320–324 | [10.1016/S0012-821X(68)80059-7](<https://doi.org/10.1016/S0012-821X(68)80059-7>) | Regressão original com erros correlacionados (rho) entre x e y |
| York, D., Evensen, N.M., López Martínez, M., De Basabe Delgado, J. (2004). Unified equations for the slope, intercept, and standard errors of the best straight line. American Journal of Physics 72, 367–375 | [10.1119/1.1632486](https://doi.org/10.1119/1.1632486) | Versão iterativa pronta para código: inclinação, intercepto e erros-padrão |
| Ludwig, K.R. (1980). Calculation of uncertainties of U-Pb isotope data. EPSL 46, 212–220 | [10.1016/0012-821X(80)90007-2](<https://doi.org/10.1016/0012-821X(80)90007-2>) | Como calcular erros e a correlação (rho) das razões 206/238 e 207/235 a partir das medidas |
| Ludwig, K.R. (2000). Decay constant errors in U–Pb concordia-intercept ages. Chemical Geology 166, 315–318 | [10.1016/S0009-2541(99)00219-3](<https://doi.org/10.1016/S0009-2541(99)00219-3>) | Como somar a incerteza das constantes de decaimento aos interceptos da discórdia |

## Correção de Pb comum e desequilíbrio

O software precisa de três correções de Pb comum (204Pb, 207Pb e 208Pb), todas alimentadas pela composição do modelo de Stacey & Kramers (1975) na idade do grão, e de uma correção opcional de 230Th para zircões jovens (menos de \~50 Ma).

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Stacey, J.S., Kramers, J.D. (1975). Approximation of terrestrial lead isotope evolution by a two-stage model. EPSL 26, 207–221 | [10.1016/0012-821X(75)90088-6](<https://doi.org/10.1016/0012-821X(75)90088-6>) | Composição do Pb comum (206/204, 207/204, 208/204) em função da idade; parâmetros prontos para código |
| Andersen, T. (2002). Correction of common lead in U–Pb analyses that do not report 204Pb. Chemical Geology 192, 59–79 | [10.1016/S0009-2541(02)00195-X](<https://doi.org/10.1016/S0009-2541(02)00195-X>) | Correção sem 204Pb, útil em LA-ICP-MS (interferência do 204Hg), resolvendo Pb comum e perda de Pb juntos |
| Williams, I.S. (1998). U-Th-Pb geochronology by ion microprobe. Reviews in Economic Geology 7, 1–35 (livro da SEG; DOI não conferido) | — | Referência clássica das correções por 204Pb, 207Pb e 208Pb e da calibração Pb/U no SHRIMP |
| Schärer, U. (1984). The effect of initial 230Th disequilibrium on young U-Pb ages: the Makalu case, Himalaya. EPSL 67, 191–204 | [10.1016/0012-821X(84)90114-6](<https://doi.org/10.1016/0012-821X(84)90114-6>) | Correção da idade 206Pb/238U pelo déficit inicial de 230Th, usando Th/U do mineral e do magma |

## Idade concórdia, média ponderada e MSWD

O software deve oferecer dois resultados por amostra: a idade concórdia de Ludwig (1998), que usa 206/238 e 207/235 juntos, e a média ponderada com MSWD, aceitando o MSWD só dentro do intervalo esperado para n análises (Wendt & Carl 1991).

```latex
\bar{t} = \frac{\sum t_i/\sigma_i^2}{\sum 1/\sigma_i^2} \qquad \sigma_{\bar{t}} = \left(\sum 1/\sigma_i^2\right)^{-1/2} \qquad \mathrm{MSWD} = \frac{1}{n-1}\sum \frac{(t_i - \bar{t})^2}{\sigma_i^2}
```

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Ludwig, K.R. (1998). On the treatment of concordant uranium-lead ages. Geochimica et Cosmochimica Acta 62, 665–676 | [10.1016/S0016-7037(98)00059-3](<https://doi.org/10.1016/S0016-7037(98)00059-3>) | Algoritmo da idade concórdia e do teste de concordância (MSWD de equivalência e de concordância) |
| Wendt, I., Carl, C. (1991). The statistical distribution of the mean squared weighted deviation. Chemical Geology 86, 275–285 | [10.1016/0168-9622(91)90010-T](<https://doi.org/10.1016/0168-9622(91)90010-T>) | Faixa aceitável do MSWD em função de n; critério para dizer se a população é única |
| Spencer, C.J., Kirkland, C.L., Taylor, R.J.M. (2016). Strategies towards statistically robust interpretations of in situ U–Pb zircon geochronology. Geoscience Frontiers 7, 581–589 | [10.1016/j.gsf.2015.11.006](https://doi.org/10.1016/j.gsf.2015.11.006) | Guia prático de MSWD, rejeição de outliers e quando reportar média ponderada |
| Vermeesch, P. (2018). IsoplotR: a free and open toolbox for geochronology. Geoscience Frontiers 9, 1479–1493 | [10.1016/j.gsf.2018.04.001](https://doi.org/10.1016/j.gsf.2018.04.001) | Média ponderada com sobredispersão (modelo de efeitos aleatórios) e regressão por máxima verossimilhança, já implementadas |

## Propagação de incertezas e reporte

O software deve separar as incertezas em níveis e reportá-las no formato x ± y/z/w (só analítica / + calibração do padrão / + constantes de decaimento), como manda Horstwood et al. (2016).

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Horstwood, M.S.A. et al. (2016). Community-derived standards for LA-ICP-MS U-(Th-)Pb geochronology: uncertainty propagation, age interpretation and data reporting. Geostandards and Geoanalytical Research 40, 311–332 | [10.1111/j.1751-908X.2016.00379.x](https://doi.org/10.1111/j.1751-908X.2016.00379.x) | Padrão da comunidade: incertezas aleatórias vs. sistemáticas, excesso de variância, tabela de dados obrigatória |
| McLean, N.M., Bowring, J.F., Bowring, S.A. (2011). An algorithm for U-Pb isotope dilution data reduction and uncertainty propagation. Geochemistry, Geophysics, Geosystems 12 | [10.1029/2010GC003478](https://doi.org/10.1029/2010GC003478) | Propagação completa por matriz de covariância (base do ET\_Redux), modelo para o motor do software |
| McLean, N.M., Condon, D.J., Schoene, B., Bowring, S.A. (2015). Evaluating uncertainties in the calibration of isotopic reference materials and multi-element isotopic tracers (EARTHTIME Tracer Calibration Part II). Geochimica et Cosmochimica Acta 164, 481–501 | [10.1016/j.gca.2015.02.040](https://doi.org/10.1016/j.gca.2015.02.040) | Como entram as incertezas do traçador e dos materiais de referência no ID-TIMS |

## Redução de dados por técnica

Cada técnica chega ao software com um tipo diferente de dado bruto: LA-ICP-MS exige correção de fracionamento ao longo do furo e normalização pelo padrão, SHRIMP exige calibração Pb/U por UO/U, e ID-TIMS exige subtração do traçador e do branco.

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Fryer, B.J., Jackson, S.E., Longerich, H.P. (1993). The application of laser ablation microprobe-ICP-MS (LAM-ICP-MS) to in situ (U)-Pb geochronology. Chemical Geology 109, 1–8 | [10.1016/0009-2541(93)90058-Q](<https://doi.org/10.1016/0009-2541(93)90058-Q>) | Primeira aplicação de LA-ICP-MS à datação U-Pb in situ |
| Jackson, S.E., Pearson, N.J., Griffin, W.L., Belousova, E.A. (2004). The application of laser ablation-inductively coupled plasma-mass spectrometry to in situ U–Pb zircon geochronology. Chemical Geology 211, 47–69 | [10.1016/j.chemgeo.2004.06.017](https://doi.org/10.1016/j.chemgeo.2004.06.017) | Protocolo LA-ICP-MS com normalização pelo padrão GJ-1; também apresenta o GJ-1 |
| Paton, C. et al. (2010). Improved laser ablation U-Pb zircon geochronology through robust downhole fractionation correction. Geochemistry, Geophysics, Geosystems 11 | [10.1029/2009GC002618](https://doi.org/10.1029/2009GC002618) | Modelo de correção do fracionamento Pb/U ao longo do furo (base do VizualAge/Iolite) |
| Košler, J., Sylvester, P.J. (2003). Present trends and the future of zircon in geochronology: laser ablation ICPMS. Reviews in Mineralogy and Geochemistry 53, 243–276 | [10.2113/0530243](https://doi.org/10.2113/0530243) | Revisão da técnica LA-ICP-MS: fracionamento, Pb comum e calibração |
| Ireland, T.R., Williams, I.S. (2003). Considerations in zircon geochronology by SIMS. Reviews in Mineralogy and Geochemistry 53, 215–242 | [10.2113/0530215](https://doi.org/10.2113/0530215) | Calibração Pb/U versus UO/U e correções no SHRIMP/SIMS |
| Parrish, R.R., Noble, S.R. (2003). Zircon U-Th-Pb geochronology by isotope dilution–thermal ionization mass spectrometry (ID-TIMS). Reviews in Mineralogy and Geochemistry 53, 183–214 | [10.2113/0530183](https://doi.org/10.2113/0530183) | Princípios da diluição isotópica, traçadores e correção de branco |
| Mattinson, J.M. (2005). Zircon U–Pb chemical abrasion (“CA-TIMS”) method: combined annealing and multi-step partial dissolution analysis for improved precision and accuracy of zircon ages. Chemical Geology 220, 47–66 | [10.1016/j.chemgeo.2005.03.011](https://doi.org/10.1016/j.chemgeo.2005.03.011) | Abrasão química que remove domínios com perda de Pb antes do ID-TIMS |

Williams (1998), McLean et al. (2011) e McLean et al. (2015), citados acima, completam SHRIMP e ID-TIMS.

## Padrões de referência de zircão

O software deve trazer uma tabela editável de padrões com idade de referência e incerteza, usada para normalizar (padrão primário) e para validar (padrão secundário) cada sessão; os valores saem dos artigos abaixo.

| Padrão | Referência | DOI | Uso típico |
| --- | --- | --- | --- |
| 91500 | Wiedenbeck, M. et al. (1995). Three natural zircon standards for U-Th-Pb, Lu-Hf, trace element and REE analyses. Geostandards Newsletter 19, 1–23 | [10.1111/j.1751-908X.1995.tb00147.x](https://doi.org/10.1111/j.1751-908X.1995.tb00147.x) | Primário em LA-ICP-MS e SIMS (\~1065 Ma) |
| GJ-1 | Jackson et al. (2004), acima | [10.1016/j.chemgeo.2004.06.017](https://doi.org/10.1016/j.chemgeo.2004.06.017) | Primário ou secundário em LA-ICP-MS (\~600 Ma) |
| Plešovice | Sláma, J. et al. (2008). Plešovice zircon — a new natural reference material for U–Pb and Hf isotopic microanalysis. Chemical Geology 249, 1–35 | [10.1016/j.chemgeo.2007.11.005](https://doi.org/10.1016/j.chemgeo.2007.11.005) | Secundário (\~337 Ma) |
| TEMORA 1 | Black, L.P. et al. (2003). TEMORA 1: a new zircon standard for Phanerozoic U–Pb geochronology. Chemical Geology 200, 155–170 | [10.1016/S0009-2541(03)00165-7](<https://doi.org/10.1016/S0009-2541(03)00165-7>) | Primário em SHRIMP (\~417 Ma) |

## Zircão detrítico e discordância

Para amostras detríticas o software precisa de três coisas além da idade de cada grão: escolher entre 206Pb/238U e 207Pb/206Pb (em geral troca-se perto de 1,0–1,5 Ga), filtrar por discordância com uma definição explícita, e desenhar a distribuição de idades (KDE) e a idade máxima de deposição.

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Gehrels, G. (2014). Detrital zircon U-Pb geochronology applied to tectonics. Annual Review of Earth and Planetary Sciences 42, 127–149 | [10.1146/annurev-earth-050212-124012](https://doi.org/10.1146/annurev-earth-050212-124012) | Fluxo completo para detríticos: escolha da idade, filtros, gráficos e comparação entre amostras |
| Fedo, C.M., Sircombe, K.N., Rainbird, R.H. (2003). Detrital zircon analysis of the sedimentary record. Reviews in Mineralogy and Geochemistry 53, 277–303 | [10.2113/0530277](https://doi.org/10.2113/0530277) | Amostragem, número de grãos e vieses na interpretação de proveniência |
| Vermeesch, P. (2012). On the visualisation of detrital age distributions. Chemical Geology 312–313, 190–194 | [10.1016/j.chemgeo.2012.04.021](https://doi.org/10.1016/j.chemgeo.2012.04.021) | KDE com largura de banda adaptativa no lugar do PDP; algoritmo pronto |
| Vermeesch, P. (2021). On the treatment of discordant detrital zircon U–Pb data. Geochronology 3, 247–257 | [10.5194/gchron-3-247-2021](https://doi.org/10.5194/gchron-3-247-2021) | Compara as definições de discordância e propõe a distância de Aitchison; mostra como o filtro muda o resultado |
| Dickinson, W.R., Gehrels, G.E. (2009). Use of U-Pb ages of detrital zircons to infer maximum depositional ages of strata: a test against a Colorado Plateau Mesozoic database. EPSL 288, 115–125 | [10.1016/j.epsl.2009.09.013](https://doi.org/10.1016/j.epsl.2009.09.013) | Definições de idade máxima de deposição (grão mais jovem, YC1σ, YC2σ etc.) |

## Th-Pb (208Pb/232Th) em zircão

A idade 208Pb/232Th usa a mesma forma de equação, com λ232 = 4,9475 × 10⁻¹¹ a⁻¹ (Le Roux & Glendenin 1963, valor adotado por Steiger & Jäger 1977 e pelo IsoplotR). Em zircão, com Th/U baixo, ela serve mais como checagem e para a correção de Pb comum por 208Pb.

```latex
\frac{^{208}\mathrm{Pb}^*}{^{232}\mathrm{Th}} = e^{\lambda_{232} t} - 1
```

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Le Roux, L.J., Glendenin, L.E. (1963). Half-life of 232Th. Proceedings of the National Meeting on Nuclear Energy, Pretoria, p. 83–94 | sem DOI (anais) | Meia-vida do 232Th usada na convenção de 1977 |
| Steiger & Jäger (1977), na seção de constantes | [10.1016/0012-821X(77)90060-7](<https://doi.org/10.1016/0012-821X(77)90060-7>) | Fixa λ232 junto com as constantes do U |
| Williams (1998), na seção de Pb comum | — | Idade 208Pb/232Th no SHRIMP e correção por 208Pb |

## U-Th por desequilíbrio (230Th/238U) em zircão jovem

Para zircões com menos de \~350 ka o relógio é o retorno ao equilíbrio secular entre 230Th e 238U; o software calcula idades-modelo de dois pontos (cristal e magma) ou isócronas no diagrama (230Th/232Th) vs. (238U/232Th), com meia-vida do 230Th em vez das do U.

```latex
\left(\frac{^{230}\mathrm{Th}}{^{232}\mathrm{Th}}\right) = \left(\frac{^{230}\mathrm{Th}}{^{232}\mathrm{Th}}\right)_0 e^{-\lambda_{230} t} + \left(\frac{^{238}\mathrm{U}}{^{232}\mathrm{Th}}\right)\left(1 - e^{-\lambda_{230} t}\right)
```

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Reid, M.R., Coath, C.D., Harrison, T.M., McKeegan, K.D. (1997). Prolonged residence times for the youngest rhyolites associated with Long Valley Caldera: 230Th–238U ion microprobe dating of young zircons. EPSL 150, 27–39 | [10.1016/S0012-821X(97)00077-0](<https://doi.org/10.1016/S0012-821X(97)00077-0>) | Método original de datação 230Th-238U em zircão por SIMS, com isócrona e idade-modelo |
| Schmitt, A.K. (2011). Uranium series accessory crystal dating of magmatic processes. Annual Review of Earth and Planetary Sciences 39, 321–349 | [10.1146/annurev-earth-040610-133330](https://doi.org/10.1146/annurev-earth-040610-133330) | Revisão das equações U-série, correção de desequilíbrio e limites de idade |
| Schmitt, A.K., Vazquez, J.A. (2017). Secondary ionization mass spectrometry analysis in petrochronology. Reviews in Mineralogy and Geochemistry 83, 199–230 (DOI não conferido) | — | Protocolos SIMS para U-Th e U-Pb em zircão jovem |
| Schärer (1984), na seção de Pb comum | [10.1016/0012-821X(84)90114-6](<https://doi.org/10.1016/0012-821X(84)90114-6>) | Liga U-Th ao U-Pb: correção de 230Th na idade 206Pb/238U |

## Pb-Pb por evaporação em zircão

A evaporação de Pb em TIMS dá só a idade 207Pb/206Pb, sem medir U; o software trata o resultado como uma idade 207Pb/206Pb comum no módulo 2. (U-Th)/He e traços de fissão saíram do documento porque não usam Pb.

| Referência | DOI | O que traz para o cálculo |
| --- | --- | --- |
| Kober, B. (1986). Whole-grain evaporation for 207Pb/206Pb-age-investigations on single zircons using a double-filament thermal ion source. Contributions to Mineralogy and Petrology 93, 482–490 | [10.1007/BF00375526](https://doi.org/10.1007/BF00375526) | Idade 207Pb/206Pb por evaporação em TIMS, por etapas de temperatura |

## Softwares de referência para validar os cálculos

O IsoplotR é o gabarito: é aberto, documenta cada algoritmo e traz conjuntos de dados de exemplo; cada função do software novo deve reproduzir os resultados dele dentro do arredondamento.

| Software | Referência | DOI ou link | Para que serve na validação |
| --- | --- | --- | --- |
| IsoplotR | Vermeesch (2018), Geoscience Frontiers 9, 1479–1493 | [10.1016/j.gsf.2018.04.001](https://doi.org/10.1016/j.gsf.2018.04.001) | Concórdia, discórdia, médias, KDE, U-Th e Th-Pb; código R aberto |
| Isoplot 3/4 | Ludwig, K.R. (2012). User's manual for Isoplot 3.75. Berkeley Geochronology Center Special Publication 5 | sem DOI | Ferramenta clássica do Excel; a maioria dos dados publicados foi calculada com ela |
| Iolite | Paton, C., Hellstrom, J., Paul, B., Woodhead, J., Hergt, J. (2011). Iolite: freeware for the visualisation and processing of mass spectrometric data. Journal of Analytical Atomic Spectrometry 26, 2508–2518 | [10.1039/c1ja10172b](https://doi.org/10.1039/c1ja10172b) | Redução de dados brutos de LA-ICP-MS (a etapa antes do cálculo de idade) |
| ET\_Redux | McLean et al. (2011), G-cubed 12 | [10.1029/2010GC003478](https://doi.org/10.1029/2010GC003478) | Redução e propagação de incertezas em ID-TIMS |

## Métodos estatísticos para U-Pb-Th em zircão

Os métodos estatísticos respondem a seis perguntas sobre uma datação: quantos grãos bastam, se a seleção enviesou o resultado, quanta confiança tem a idade, quais grãos entram no cálculo, quantas populações existem e se duas amostras são iguais. Todos trabalham sobre idades ou razões já calculadas por grão, então pertencem ao módulo 2. Os marcados como "mais usado" são os que aparecem como padrão na literatura e no IsoplotR.

| Pergunta | Método | Aplicação | Mais usado | Referência | DOI |
| --- | --- | --- | --- | --- | --- |
| Representatividade | Número mínimo de grãos para não perder uma população de fração f com dada confiança (117 grãos para f = 0,05 e 95%) | Detrítico | Sim | Vermeesch, P. (2004). How many grains are needed for a provenance study? EPSL 224, 441–451 | não conferido |
| Representatividade | Simulação numérica dos limites de detecção e resolução de populações | Detrítico | Não | Andersen, T. (2005). Detrital zircons as tracers of sedimentary provenance: limiting conditions from statistics and numerical simulation. Chemical Geology 216, 249–270 | [10.1016/j.chemgeo.2004.11.013](https://doi.org/10.1016/j.chemgeo.2004.11.013) |
| Representatividade | Grandes conjuntos (n ≥ 1000) por LA-ICP-MS e efeito de n nas distribuições | Detrítico | Não | Pullen, A. et al. (2014). What happens when n = 1000? Creating large-n geochronological datasets with LA-ICP-MS for geologic investigations. JAAS 29, 971–980 | [10.1039/c4ja00024b](https://doi.org/10.1039/c4ja00024b) |
| Viés | Viés de fertilidade em zircão, separação mineral e escolha de grãos | Detrítico | Sim | Malusà, M.G. et al. (2013). Bias associated with detrital zircon geochronology and thermochronometry. Chemical Geology 359, 90–107 | [10.1016/j.chemgeo.2013.09.016](https://doi.org/10.1016/j.chemgeo.2013.09.016) |
| Viés | Teste do viés da catação manual contra montagem em massa (bulk) | Detrítico | Não | Dröllner, M. et al. (2021). Every zircon deserves a date: selection bias in detrital geochronology. Geological Magazine 158, 1135–1142 | [10.1017/S0016756821000145](https://doi.org/10.1017/S0016756821000145) |
| Confiança | Faixa aceitável do MSWD para n grãos (teste qui-quadrado) | Todas | Sim | Wendt & Carl (1991), seção de média ponderada | [10.1016/0168-9622(91)90010-T](<https://doi.org/10.1016/0168-9622(91)90010-T>) |
| Confiança | Média com sobredispersão (efeitos aleatórios) e intervalo de confiança | Todas | Sim | Vermeesch (2018), IsoplotR | [10.1016/j.gsf.2018.04.001](https://doi.org/10.1016/j.gsf.2018.04.001) |
| Confiança | Estatística robusta e bootstrap para regressões (discórdia, isócrona) | Ígneas, metamórficas | Não | Powell, R., Hergt, J., Woodhead, J. (2002). Improving isochron calculations with robust statistics and the bootstrap. Chemical Geology 185, 191–204 | não conferido |
| Seleção objetiva de grãos | Critério de Chauvenet generalizado para rejeitar outliers da média | Ígneas, vulcânicas | Sim | Vermeesch (2018), IsoplotR | [10.1016/j.gsf.2018.04.001](https://doi.org/10.1016/j.gsf.2018.04.001) |
| Seleção objetiva de grãos | Filtro de discordância com definição explícita | Todas | Sim | Vermeesch (2021), Geochronology 3; Spencer et al. (2016) | [10.5194/gchron-3-247-2021](https://doi.org/10.5194/gchron-3-247-2021) |
| Seleção objetiva de grãos | Idade de erupção ou cristalização por amostragem bayesiana da distribuição de cristalização, sem escolher grãos à mão | Vulcânicas, cinzas | Não | Keller, C.B., Schoene, B., Samperton, K.M. (2018). A stochastic sampling approach to zircon eruption age interpretation. Geochemical Perspectives Letters 8, 31–35 | [10.7185/geochemlet.1826](https://doi.org/10.7185/geochemlet.1826) |
| Populações | Modelo de mistura: número, idade e proporção de populações (herança, picos) | Ígneas com herança, detrítico | Sim | Sambridge, M.S., Compston, W. (1994). Mixture modeling of multi-component data sets with application to ion-probe zircon ages. EPSL 128, 373–390 | [10.1016/0012-821X(94)90157-0](<https://doi.org/10.1016/0012-821X(94)90157-0>) |
| Populações | Modelo de mistura bayesiano (MCMC) com número de populações desconhecido | Ígneas com herança, detrítico | Não | Jasra, A., Stephens, D., Gallagher, K., Holmes, C. (2006). Bayesian mixture modelling in geochronology via Markov chain Monte Carlo. Mathematical Geology 38, 269–300 | [10.1007/s11004-005-9019-3](https://doi.org/10.1007/s11004-005-9019-3) |
| Idade máxima de deposição | Comparação de acurácia dos critérios (YSG, YC1σ, YC2σ, YPP, etc.) | Detrítico | Sim | Coutts, D.S., Matthews, W.A., Hubbard, S.M. (2019). Assessment of widely used methods to derive depositional ages from detrital zircon populations. Geoscience Frontiers 10, 1421–1435 | [10.1016/j.gsf.2018.11.002](https://doi.org/10.1016/j.gsf.2018.11.002) |
| Idade máxima de deposição | Estimador por máxima verossimilhança com intervalo de confiança | Detrítico | Não | Vermeesch, P. (2021). Maximum depositional age estimation revisited. Geoscience Frontiers 12, 843–850 | [10.1016/j.gsf.2020.08.008](https://doi.org/10.1016/j.gsf.2020.08.008) |
| Comparação de amostras | Testes de Kolmogorov-Smirnov e Kuiper, similaridade, likeness e correlação cruzada | Detrítico | Sim | Saylor, J.E., Sundell, K.E. (2016). Quantifying comparison of large detrital geochronology data sets. Geosphere 12, 203–220 | [10.1130/GES01237.1](https://doi.org/10.1130/GES01237.1) |
| Comparação de amostras | Medidas de dissimilaridade e suas propriedades | Detrítico | Não | Vermeesch, P. (2018). Dissimilarity measures in detrital geochronology. Earth-Science Reviews 178, 310–321 | [10.1016/j.earscirev.2017.11.027](https://doi.org/10.1016/j.earscirev.2017.11.027) |
| Comparação de amostras | Escalonamento multidimensional (MDS) de várias amostras | Detrítico | Sim | Vermeesch, P. (2013). Multi-sample comparison of detrital age distributions. Chemical Geology 341, 140–146 | [10.1016/j.chemgeo.2013.01.010](https://doi.org/10.1016/j.chemgeo.2013.01.010) |
| Comparação de amostras | Desmistura: proporção de cada área-fonte numa amostra | Detrítico | Não | Sundell, K.E., Saylor, J.E. (2017). Unmixing detrital geochronology age distributions. G-cubed 18, 2872–2886 | [10.1002/2016GC006774](https://doi.org/10.1002/2016GC006774) |
| Análise multivariada | Combinação de muitas amostras e métodos (MDS, procrustes, análise de 3 vias) | Detrítico | Não | Vermeesch, P., Garzanti, E. (2015). Making geological sense of 'Big Data' in sedimentary provenance analysis. Chemical Geology 409, 20–27 | [10.1016/j.chemgeo.2015.05.004](https://doi.org/10.1016/j.chemgeo.2015.05.004) |
| Análise multivariada | Pacote R com KS, MDS e desmistura prontos para conferir resultados | Detrítico | Não | Vermeesch, P., Resentini, A., Garzanti, E. (2016). An R package for statistical provenance analysis. Sedimentary Geology 336, 14–25 | [10.1016/j.sedgeo.2016.01.009](https://doi.org/10.1016/j.sedgeo.2016.01.009) |

Geoestatística espacial (krigagem, variogramas) não aparece como método estabelecido para idades U-Pb-Th em zircão: só achei aplicações a isótopos de Hf e Nd, sem artigo publicado com DOI, então ficou de fora. A parte "geo" desta lista é a análise multivariada de proveniência (MDS e desmistura).

## Índice por aplicação geológica

As referências de cálculo (constantes, concórdia, regressão, Pb comum, incertezas) valem para todas as aplicações; a tabela lista o que é específico de cada uma, incluindo quatro textos de interpretação que não aparecem nas seções acima.

| Aplicação | O que o software precisa | Referências de cálculo | Referências estatísticas |
| --- | --- | --- | --- |
| Bacias sedimentares e proveniência (zircão detrítico) | Idade por grão, filtro de discordância, KDE, idade máxima de deposição, comparação entre amostras | Gehrels 2014; Fedo et al. 2003; Vermeesch 2012; Vermeesch 2021; Dickinson & Gehrels 2009; Andersen 2002 | Vermeesch 2004; Andersen 2005; Pullen et al. 2014; Malusà et al. 2013; Dröllner et al. 2021; Coutts et al. 2019; Vermeesch 2021 (MDA); Saylor & Sundell 2016; Vermeesch 2013; Vermeesch 2018 (dissimilaridade); Sundell & Saylor 2017; Vermeesch & Garzanti 2015 |
| Granitos e rochas ígneas (cristalização) | Idade concórdia ou média ponderada, separação de herança e perda de Pb | Ludwig 1998; Wendt & Carl 1991; Spencer et al. 2016; Schaltegger et al. 2015; Hoskin & Schaltegger 2003 ([10.2113/0530027](https://doi.org/10.2113/0530027)); Corfu et al. 2003, Atlas of zircon textures, RiMG 53, 469–500 ([10.2113/0530469](https://doi.org/10.2113/0530469)); Barboni et al. 2013, Chemical Geology 342, 76–93 ([10.1016/j.chemgeo.2012.12.011](https://doi.org/10.1016/j.chemgeo.2012.12.011)) | Chauvenet generalizado e efeitos aleatórios (Vermeesch 2018); Sambridge & Compston 1994; Jasra et al. 2006; Powell et al. 2002 |
| Rochas metamórficas | Datar sobrecrescimentos e ligar idade a condições metamórficas; discórdia com intercepto inferior | Rubatto 2002, Chemical Geology 184, 123–138 ([10.1016/S0009-2541(01)00355-2](<https://doi.org/10.1016/S0009-2541(01)00355-2>)); Hoskin & Schaltegger 2003; York 2004; Ludwig 2000 | Sambridge & Compston 1994; Powell et al. 2002 |
| Estratigrafia de alta precisão (cinzas vulcânicas) | CA-ID-TIMS, incertezas x/y/z, constantes e 238U/235U atualizados | Bowring & Schmitz 2003, RiMG 53, 305–326 ([10.2113/0530305](https://doi.org/10.2113/0530305)); Mattinson 2005; McLean et al. 2011; McLean et al. 2015; Hiess et al. 2012 | Keller et al. 2018; Vermeesch 2018 |
| Vulcânicas jovens e câmaras magmáticas (< \~350 ka) | Isócrona 230Th-238U e correção de desequilíbrio em U-Pb | Reid et al. 1997; Schmitt 2011; Schmitt & Vazquez 2017; Schärer 1984 | Keller et al. 2018; Sambridge & Compston 1994 |

## Índice por método de aquisição

O software deve perguntar a técnica logo na importação, porque ela define o formato dos dados, as correções e o nível de incerteza esperado.

| Método de aquisição | O que muda no cálculo | Referências de cálculo | Referências estatísticas |
| --- | --- | --- | --- |
| LA-ICP-MS | Fracionamento ao longo do furo, normalização por padrão, Pb comum sem 204Pb, excesso de variância | Fryer et al. 1993; Jackson et al. 2004; Paton et al. 2010; Paton et al. 2011 (Iolite); Košler & Sylvester 2003; Andersen 2002; Horstwood et al. 2016 | Pullen et al. 2014 (n grande); Vermeesch 2004; Spencer et al. 2016 |
| SHRIMP / SIMS | Calibração Pb/U por UO/U, correções por 204Pb, 207Pb ou 208Pb, padrão TEMORA ou 91500 | Williams 1998; Ireland & Williams 2003; Black et al. 2003; Wiedenbeck et al. 1995; Reid et al. 1997 e Schmitt & Vazquez 2017 (U-Th por SIMS) | Sambridge & Compston 1994 (criado para dados SHRIMP) |
| ID-TIMS (diluição isotópica) | Subtração de traçador e branco, propagação completa por covariância | Parrish & Noble 2003; McLean et al. 2011 (ET\_Redux); McLean et al. 2015 | Powell et al. 2002 |
| CA-ID-TIMS (abrasão química) | Igual ao ID-TIMS, com remoção prévia de zonas com perda de Pb | Mattinson 2005; Bowring & Schmitz 2003; Barboni et al. 2013 | Keller et al. 2018 |
| Evaporação de Pb em TIMS (Kober) | Só idade 207Pb/206Pb, sem U | Kober 1986 | Wendt & Carl 1991 (média das etapas) |

Os métodos estatísticos de comparação de amostras e de viés não dependem da técnica: valem para qualquer tabela de idades por grão.

## Métodos de cálculo mais usados

O software se divide em dois módulos: o módulo 1 transforma leituras do equipamento em razões e idades por grão; o módulo 2 transforma idades por grão em idades de amostra. Um detalhe pesa no projeto: concórdia e discórdia precisam das razões, dos erros e da correlação rho de cada grão, não só da idade, então o software deve pedir ao laboratório a tabela completa (formato de Horstwood et al. 2016).

### Módulo 1: a partir das leituras de cada elemento e isótopo

As idades U-Pb saem de razões isotópicas; as concentrações (ppm de U, Th, Pb) servem para Th/U e para avaliar o grão.

1. Subtração do branco ou do sinal de fundo e cálculo das razões medidas 206Pb/238U, 207Pb/206Pb, 208Pb/232Th (todas as técnicas).
2. Correção de fracionamento e normalização pelo padrão primário (LA-ICP-MS: Paton et al. 2010; SHRIMP: calibração UO/U, Williams 1998); no ID-TIMS, subtração do traçador (McLean et al. 2011).
3. Cálculo de 207Pb/235U = 207Pb/206Pb × 206Pb/238U × 137,818 quando ele não é medido diretamente (Hiess et al. 2012).
4. Incertezas de cada razão e correlação rho entre 206/238 e 207/235 (Ludwig 1980).
5. Correção de Pb comum: por 204Pb, por 207Pb ou por 208Pb, com Pb comum de Stacey & Kramers (1975); sem 204Pb, Andersen (2002).
6. Correção de desequilíbrio 230Th para zircões jovens (Schärer 1984).
7. Idades aparentes 206Pb/238U, 207Pb/235U, 207Pb/206Pb e 208Pb/232Th (Jaffey et al. 1971; Steiger & Jäger 1977).
8. Grau de discordância e razão Th/U de cada grão (Vermeesch 2021).
9. Concentrações de U, Th e Pb em ppm por comparação com o padrão de concentração conhecida (Jackson et al. 2004).

### Módulo 2: a partir das idades ou razões já calculadas grão a grão

1. Escolha da melhor idade por grão: 206Pb/238U para grãos jovens e 207Pb/206Pb para antigos (Gehrels 2014).
2. Filtro de discordância com limite explícito (Vermeesch 2021).
3. Média ponderada com MSWD e teste pela faixa aceitável de Wendt & Carl (1991); com sobredispersão, modelo de efeitos aleatórios (Vermeesch 2018).
4. Idade concórdia com MSWD de concordância e de equivalência (Ludwig 1998).
5. Discórdia com interceptos superior e inferior por regressão de York (York et al. 2004; Ludwig 2000).
6. Regressão no Tera-Wasserburg ancorada no Pb comum, para grãos com Pb comum alto (Tera & Wasserburg 1972).
7. Histograma e KDE das idades detríticas (Vermeesch 2012).
8. Idade máxima de deposição: grão mais jovem, YC1σ, YC2σ (Dickinson & Gehrels 2009).
9. Para U-Th, isócrona 230Th-238U de vários grãos (Reid et al. 1997).

Os itens 3 a 8 do módulo 2 cobrem a maior parte dos artigos publicados com U-Pb em zircão: média ponderada e concórdia para ígneas, discórdia para metamórficas e herança, KDE e idade máxima de deposição para bacias.

### Módulo 2, estatística: os mais usados

1. Teste do MSWD pela faixa de Wendt & Carl (1991) e média com efeitos aleatórios quando há sobredispersão (Vermeesch 2018).
2. Rejeição objetiva de outliers pelo critério de Chauvenet generalizado (Vermeesch 2018) e filtro de discordância (Vermeesch 2021).
3. Modelo de mistura para separar populações e herança (Sambridge & Compston 1994).
4. Aviso de representatividade pelo número de grãos (Vermeesch 2004).
5. Teste de Kolmogorov-Smirnov e MDS para comparar amostras detríticas (Saylor & Sundell 2016; Vermeesch 2013).
6. Critério de idade máxima de deposição com acurácia avaliada (Coutts et al. 2019).

## Menu de opções do software

Cada escolha do usuário vira uma lista no software, e cada opção carrega sua referência, que sai impressa junto com o resultado para ir direto para a seção de métodos do artigo.

| Etapa | O que o usuário escolhe | Opções (padrão primeiro) | Referência de cada opção |
| --- | --- | --- | --- |
| Entrada | Tipo de dado | Razões por grão com erros e rho; idades por grão; leituras brutas | Horstwood et al. 2016 (formato da tabela) |
| Entrada | Técnica de aquisição | LA-ICP-MS; SHRIMP/SIMS; ID-TIMS; CA-ID-TIMS | Ver Índice por método de aquisição |
| Entrada | Formato dos erros | 2σ ou 1σ; absoluto ou % | Horstwood et al. 2016 |
| Constantes | Constantes de decaimento | Jaffey; personalizada | Jaffey et al. 1971; Steiger & Jäger 1977 |
| Constantes | 238U/235U | 137,818; 137,88 | Hiess et al. 2012; Steiger & Jäger 1977 |
| Pb comum | Correção | Nenhuma; 204Pb; 207Pb; 208Pb; Andersen | Williams 1998; Andersen 2002 |
| Pb comum | Composição do Pb comum | Stacey & Kramers na idade do grão; valor do usuário | Stacey & Kramers 1975 |
| Desequilíbrio | Correção de 230Th | Não; sim, com Th/U do magma | Schärer 1984 |
| Idade do grão | Idade preferida | 206/238 abaixo de um corte e 207/206 acima (corte padrão 1,0 Ga, editável); só 206/238; só 207/206 | Gehrels 2014 |
| Filtro | Definição de discordância | Distância de Aitchison; % relativa 206/238 vs 207/206; probabilidade de concordância | Vermeesch 2021; Ludwig 1998 |
| Filtro | Limite de discordância | 10%; valor do usuário | Vermeesch 2021; Spencer et al. 2016 |
| Cálculo de amostra | O que calcular | Média ponderada; idade concórdia; discórdia; Tera-Wasserburg ancorada; KDE; idade máxima de deposição; isócrona 230Th-238U | Wendt & Carl 1991; Ludwig 1998; York et al. 2004; Tera & Wasserburg 1972; Vermeesch 2012; Dickinson & Gehrels 2009; Reid et al. 1997 |
| Média ponderada | Tratamento da sobredispersão | Efeitos aleatórios; multiplicar o erro por √MSWD; nenhum | Vermeesch 2018; Wendt & Carl 1991 |
| Idade máxima de deposição | Critério | YC2σ; YC1σ; grão mais jovem | Dickinson & Gehrels 2009 |
| Incertezas | Nível reportado | x ± y/z/w (analítica / + padrão / + constantes); só analítica | Horstwood et al. 2016; Ludwig 2000 |
| Gráficos | Diagrama | Wetherill; Tera-Wasserburg; KDE com histograma; média ponderada em barras | Wetherill 1956; Tera & Wasserburg 1972; Vermeesch 2012 |

Opções estatísticas do menu:

| Etapa | O que o usuário escolhe | Opções (padrão primeiro) | Referência de cada opção |
| --- | --- | --- | --- |
| Seleção de grãos | Rejeição de outliers | Chauvenet generalizado; nenhuma; manual com justificativa | Vermeesch 2018 |
| Seleção de grãos | Idade de erupção ou cristalização | Média ponderada; grãos mais jovens coerentes; amostragem bayesiana | Wendt & Carl 1991; Keller et al. 2018 |
| Representatividade | Aviso de número de grãos | Fração 0,05 com 95%; valores do usuário | Vermeesch 2004 |
| Populações | Separação de populações | Modelo de mistura com n escolhido por critério; bayesiano | Sambridge & Compston 1994; Jasra et al. 2006 |
| Idade máxima de deposição | Estimador | YC2σ; YC1σ; grão mais jovem; máxima verossimilhança | Dickinson & Gehrels 2009; Coutts et al. 2019; Vermeesch 2021 (MDA) |
| Comparação de amostras | Teste ou medida | Kolmogorov-Smirnov; Kuiper; likeness; MDS | Saylor & Sundell 2016; Vermeesch 2018 (dissimilaridade); Vermeesch 2013 |
| Comparação de amostras | Desmistura de fontes | Não; sim | Sundell & Saylor 2017 |
| Confiança | Intervalo de regressão | Analítico (York); bootstrap robusto | York et al. 2004; Powell et al. 2002 |

## Próximo passo do software

Comece pelo módulo 2 com o menu acima, porque a maioria dos laboratórios já entrega a tabela de razões e idades por grão. A planilha de entrada está definida na seção seguinte; o conjunto de teste com os dados de exemplo do IsoplotR 7.1, nos formatos aceitos, e os resultados de referência calculados pelo próprio IsoplotR estão na pasta teste-modulo2 do projeto.

## Planilha de entrada do módulo 2

O software lê uma linha por análise (spot ou grão) e uma coluna por variável; só o identificador é obrigatório, e cada cálculo do menu fica disponível ou bloqueado conforme as colunas que existirem.

### Colunas

| Coluna | Unidade ou forma | Nomes reconhecidos (exemplos) | Necessária para |
| --- | --- | --- | --- |
| Amostra | texto | Sample, Amostra | Agrupar análises |
| Análise | texto | Spot, Analysis, Grain, Grão | Tudo (obrigatória) |
| 207Pb/235U e erro | razão | 207/235, Pb207/U235, 7/35 | Concórdia de Wetherill, discórdia |
| 206Pb/238U e erro | razão | 206/238, Pb206/U238, 6/38 | Concórdia, discórdia, idade 206/238 |
| rho (correlação dos erros) | -1 a 1 | rho, Rho 6/8-7/5, error corr. | Concórdia e discórdia |
| 238U/206Pb e erro | razão | 238/206, U238/Pb206 | Tera-Wasserburg |
| 207Pb/206Pb e erro | razão | 207/206, Pb207/Pb206, 7/6 | Tera-Wasserburg, idade 207/206 |
| 208Pb/232Th e erro | razão | 208/232, Pb208/Th232 | Idade Th-Pb |
| 204Pb ou f206 (%) | cps, razão ou % | 204Pb, 206Pb/204Pb, f206 | Correção de Pb comum |
| U, Th, Pb | ppm | U ppm, Th (ppm), Pb\* | Th/U e avaliação do grão |
| Th/U | razão | Th/U, Th\_U | Avaliação do grão, correção de 230Th |
| Idades 206/238, 207/235, 207/206, 208/232 e erros | Ma | Age 6/38, Idade 206Pb/238U | Média ponderada, KDE, MDA, estatística |
| Discordância | % | Disc., Conc. %, Discordance | Filtro (recalculada se as razões existirem) |
| (230Th/232Th), (238U/232Th), erros e rho | razão de atividade | Th230/Th232, U238/Th232 | Isócrona U-Th |

Com só as idades por grão ficam liberados média ponderada, MSWD, KDE, idade máxima de deposição e a estatística; concórdia e discórdia exigem as razões, os erros e o rho. Se o rho faltar, o software usa rho = 0 e avisa que a elipse fica aproximada.

### Perguntas feitas uma vez por arquivo

1. Técnica de aquisição: LA-ICP-MS, SHRIMP/SIMS, ID-TIMS, CA-ID-TIMS ou evaporação.
2. Nível dos erros: 1σ ou 2σ, absolutos ou em %.
3. Se os erros já incluem as incertezas sistemáticas (padrão e constantes).
4. Se as razões já vêm corrigidas de Pb comum, e por qual método.
5. Que constantes e razão 238U/235U o laboratório usou nas idades.

### Regras de importação

1. Formatos aceitos: .xlsx, .xls, .ods, .csv e .txt; num arquivo com várias abas, o usuário escolhe a aba.
2. Em .xlsx, .xls e .ods os números já vêm como números; se uma célula vier como texto (ex.: "0,0512"), ela é convertida pela regra do item 3.
3. Em .csv e .txt o software detecta o separador de colunas (vírgula, ponto e vírgula, tabulação) e o decimal (ponto ou vírgula) olhando as primeiras linhas: se as colunas são separadas por ponto e vírgula, o decimal provavelmente é vírgula. Quando a detecção for ambígua, ele pergunta.
4. Separador de milhar ("1.234,5" ou "1,234.5") é reconhecido e removido.
5. Codificação de texto UTF-8 ou Latin-1 detectada automaticamente, para que ±, σ e acentos não quebrem.
6. Cabeçalho em mais de uma linha e linhas de título acima da tabela são comuns em planilhas de laboratório: o usuário marca a linha do cabeçalho na prévia.
7. Valores como "\<LOD", "n.d.", "bdl", "-" ou célula vazia viram "sem dado", nunca zero.
8. Antes de calcular, o software mostra a prévia com as colunas reconhecidas; o usuário confirma ou corrige numa lista.
9. O mapeamento confirmado pode ser salvo como perfil do laboratório, para o próximo arquivo do mesmo laboratório entrar sem perguntas.
10. Toda conversão (2σ para 1σ, % para absoluto, recálculo da discordância) fica registrada no relatório de saída, com a referência do método.

## Como as referências foram conferidas

Os DOIs foram conferidos no Crossref ou em páginas de repositórios institucionais e editoras (NERC, UCL, Princeton, Macquarie, Arizona, USGS, Copernicus, RSC). Os capítulos do volume Zircon (Reviews in Mineralogy and Geochemistry 53) foram conferidos no sumário da [MSA](https://msaweb.org/volume-53-zircon/); só o DOI de Hoskin & Schaltegger foi confirmado diretamente, e os demais seguem o mesmo padrão da série (10.2113/053 + página inicial). Ficaram sem DOI conferido: Williams 1998, Le Roux & Glendenin 1963, Schmitt & Vazquez 2017, Vermeesch 2004, Powell et al. 2002 e o manual do Isoplot. O escopo é só datação por isótopos de U, Th e Pb em zircão (U-Pb, Th-Pb, Pb-Pb, U-Th).
