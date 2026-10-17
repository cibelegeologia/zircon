"""Constantes de decaimento e razões isotópicas usadas nos cálculos.

Valores iguais aos do IsoplotR 7.1, para que os resultados possam ser
conferidos contra ele.
"""

# Constantes de decaimento em 1/Ma
LAMBDA_238 = 1.55125e-4   # Jaffey et al. (1971)
LAMBDA_235 = 9.8485e-4    # Jaffey et al. (1971)
LAMBDA_232 = 4.9475e-5    # Le Roux e Glendenin (1963); Steiger e Jäger (1977)

# Razão natural 238U/235U
U238_U235 = 137.818       # Hiess et al. (2012)

REFERENCIAS = {
    "LAMBDA_238": "JAFFEY, A. H. et al. Physical Review C, v. 4, p. 1889-1906, 1971.",
    "LAMBDA_235": "JAFFEY, A. H. et al. Physical Review C, v. 4, p. 1889-1906, 1971.",
    "LAMBDA_232": "LE ROUX, L. J.; GLENDENIN, L. E. 1963; STEIGER, R. H.; JÄGER, E. 1977.",
    "U238_U235": "HIESS, J. et al. Science, v. 335, p. 1610-1614, 2012.",
}
