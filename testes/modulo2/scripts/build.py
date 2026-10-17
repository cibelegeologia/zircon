import pandas as pd, os, sys, csv
S=sys.argv[1]; OUT=sys.argv[2]; I=f"{S}/isoplotr"
E=f"{OUT}/entrada"; os.makedirs(E,exist_ok=True)
ren={ # IsoplotR -> nomes da planilha de entrada
 'Pb207U235':'207Pb/235U','sePb207U235':'erro 207Pb/235U','errPb207U235':'erro 207Pb/235U',
 'Pb206U238':'206Pb/238U','sePb206U238':'erro 206Pb/238U','errPb206U238':'erro 206Pb/238U',
 'U238Pb206':'238U/206Pb','errU238Pb206':'erro 238U/206Pb','seU238Pb206':'erro 238U/206Pb',
 'Pb207Pb206':'207Pb/206Pb','errPb207Pb206':'erro 207Pb/206Pb','sePb207Pb206':'erro 207Pb/206Pb',
 'Pb204U238':'204Pb/238U','errPb204U238':'erro 204Pb/238U',
 'Pb208Th232':'208Pb/232Th','sePb208Th232':'erro 208Pb/232Th','Th232U238':'232Th/238U','seTh232U238':'erro 232Th/238U',
 'Th232Pb204':'232Th/204Pb','errTh232Pb204':'erro 232Th/204Pb','Pb208Pb204':'208Pb/204Pb','errPb208Pb204':'erro 208Pb/204Pb',
 'Pb206Pb204':'206Pb/204Pb','errPb206Pb204':'erro 206Pb/204Pb','Pb207Pb204':'207Pb/204Pb','errPb207Pb204':'erro 207Pb/204Pb',
 '8/2':'(238U/232Th)','s[8/2]':'erro (238U/232Th)','4/2':'(234U/232Th)','s[4/2]':'erro (234U/232Th)','0/2':'(230Th/232Th)','s[0/2]':'erro (230Th/232Th)',
 'rXY':'rho XY','rXZ':'rho XZ','rYZ':'rho YZ','rho':'rho','rWX':'rho WX','rWY':'rho WY','rWZ':'rho WZ'}
sets={'UPb1':'U-Pb Wetherill (discordante)','UPb2':'U-Pb Tera-Wasserburg','UPb4':'U-Pb com 204Pb (Pb comum)','UPb7':'U-Pb-Th com 208Pb (Pb comum)','ThPb1':'Th-Pb isocrona','PbPb1':'Pb-Pb isocrona','ThU1':'U-Th isocrona'}
def write_all(df,name):
    df.to_excel(f"{E}/{name}.xlsx",index=False)
    df.to_csv(f"{E}/{name}_virgula-ponto.csv",index=False)                       # separador , decimal .
    df.to_csv(f"{E}/{name}_pontoevirgula-virgula.csv",index=False,sep=';',decimal=',')  # padrao pt-BR
    df.to_csv(f"{E}/{name}_tab.txt",index=False,sep='\t')
for k,desc in sets.items():
    df=pd.read_csv(f"{I}/inst_{k}.csv",dtype=str)
    df=df.apply(lambda c: pd.to_numeric(c))
    df=df.rename(columns=ren)
    df.insert(0,'Analise',[f"{k}-{i+1:02d}" for i in range(len(df))]); df.insert(0,'Amostra',k)
    write_all(df,k)
# idades por grao (saida do IsoplotR para UPb1) como entrada so-de-idades
ag=pd.read_csv(f"{S}/out3/idades_por_grao_UPb1.csv")
ag=ag.rename(columns={'t.75':'Idade 207Pb/235U (Ma)','err[t.75]':'erro (Ma)','t.68':'Idade 206Pb/238U (Ma)','err[t.68]':'erro (Ma).1','t.76':'Idade 207Pb/206Pb (Ma)','err[t.76]':'erro (Ma).2','t.conc':'Idade concordia (Ma)','err[t.conc]':'erro (Ma).3'}).drop(columns=['p[conc]'])
ag.columns=[c.split('.')[0] if c.startswith('erro') else c for c in ag.columns]
ag.insert(0,'Analise',[f"UPb1-{i+1:02d}" for i in range(len(ag))]); ag.insert(0,'Amostra','UPb1')
write_all(ag.round(6),'UPb1_so_idades')
# detritico: formato longo (amostra, idade)
dz=pd.read_csv(f"{I}/inst_DZ.csv")
long=dz.melt(var_name='Amostra',value_name='Idade 206Pb/238U ou 207Pb/206Pb (Ma)').dropna()
long.insert(1,'Analise',long.groupby('Amostra').cumcount()+1)
write_all(long,'DZ_detritico_so_idades')
# variante "laboratorio baguncado": titulo, cabecalho em 2 linhas, erros 2s %, ; e virgula decimal, Latin-1
df=pd.read_csv(f"{I}/inst_UPb1.csv")
v=pd.DataFrame({'Spot':[f"Zr-{i+1:02d}" for i in range(len(df))],
 'Pb207/U235':df.Pb207U235,'± 2s %':200*df.sePb207U235/df.Pb207U235,
 'Pb206/U238':df.Pb206U238,'± 2s % ':200*df.sePb206U238/df.Pb206U238,'Rho':df.rXY})
with open(f"{E}/UPb1_estilo_laboratorio_latin1.csv","w",encoding="latin-1",newline="") as fh:
    w=csv.writer(fh,delimiter=';')
    w.writerow(['Laboratório de Geocronologia - Relatório de análise']); w.writerow(['Amostra: UPb1   Sessão: exemplo']); w.writerow([])
    w.writerow(['','Razões isotópicas','','','','Correlação'])
    w.writerow([c.strip() for c in v.columns])
    for r in v.itertuples(index=False):
        w.writerow([r[0]]+[f"{x:.6g}".replace('.',',') for x in r[1:]])
print(sorted(os.listdir(E)))
