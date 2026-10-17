.libPaths(file.path(Sys.getenv("S"),"Rlib")); suppressMessages(library(IsoplotR))
inst <- file.path(Sys.getenv("S"),"isoplotr")
rd <- function(f,...) read.data(file.path(inst,paste0("inst_",f,".csv")),ierr=1,...)
rows <- list()
add <- function(set,calc,opt,val,err=NA,mswd=NA,p=NA,n=NA,obs=""){
  rows[[length(rows)+1]] <<- data.frame(conjunto=set,calculo=calc,opcoes=opt,valor_Ma=signif(val,8),erro_1s_Ma=signif(err,6),MSWD=signif(mswd,5),p_valor=signif(p,4),n=n,observacao=obs)}
pdf(NULL)
try_ <- function(e) tryCatch(e, error=function(err) message("ERR: ",conditionMessage(err)))
# U-Pb format 1 and 2
for (f in c("UPb1","UPb2","UPb3")) {
  fmt <- as.integer(substr(f,4,4)); x <- rd(f,method="U-Pb",format=fmt)
  try_({a <- concordia(x,type=1,show.age=1,oerr=1,sigdig=10); ca <- a$age
    add(f,"Idade concórdia (Ludwig 1998)","sem Pb comum; sem erros externos",ca["t"],ca["s[t]"],a$mswd["combined"],a$p.value["combined"],length(x$x[,1]),obs=paste0("MSWD equival\u00eancia ",signif(a$mswd["equivalence"],4),"; MSWD concord\u00e2ncia ",signif(a$mswd["concordance"],4)))})
  try_({dd <- concordia(x,type=1,show.age=2,oerr=1,sigdig=10)
    add(f,"Discórdia: intercepto inferior","modelo 1, máxima verossimilhança (Ludwig 1998)",dd$par["t[l]"],dd$err["s","t[l]"],dd$mswd,dd$p.value,length(x$x[,1]))
    add(f,"Discórdia: intercepto superior","modelo 1, máxima verossimilhança (Ludwig 1998)",dd$par["t[u]"],dd$err["s","t[u]"],dd$mswd,dd$p.value,length(x$x[,1]))})
  try_({t1 <- age(x,type=1,oerr=1,sigdig=10)
    write.csv(t1,file.path(Sys.getenv("OUT"),paste0("idades_por_grao_",f,".csv")),row.names=FALSE)
    for (col in c("t.68","t.76")) if (col %in% colnames(t1)) {
      w <- weightedmean(t1[,c(col,paste0("err[",col,"]"))],random.effects=FALSE,detect.outliers=FALSE,plot=FALSE)
      add(f,paste("Média ponderada",ifelse(col=="t.68","206Pb/238U","207Pb/206Pb")),"sem outliers; sem efeitos aleatórios",w$mean["t"],w$mean["s[t]"],w$mswd,w$p.value,nrow(t1))
      w2 <- weightedmean(t1[,c(col,paste0("err[",col,"]"))],random.effects=TRUE,detect.outliers=TRUE,plot=FALSE)
      add(f,paste("Média ponderada",ifelse(col=="t.68","206Pb/238U","207Pb/206Pb")),"Chauvenet generalizado + efeitos aleatórios (Vermeesch 2018)",w2$mean["t"],w2$mean["s[t]"],w2$mswd,w2$p.value,sum(w2$valid),obs=paste("dispersão",signif(w2$disp["w"],4)))
    }})
}
# discordia detail with intercepts via age type 3
for (f in c("UPb1","UPb2")) { fmt <- as.integer(substr(f,4,4)); x <- rd(f,method="U-Pb",format=fmt)
  try_({ d <- age(x,type=3,oerr=1,sigdig=10); capture.output(print(d)) -> o
    writeLines(o, file.path(Sys.getenv("OUT"),paste0("discordia_",f,".txt"))) }) }
# common Pb formats
for (f in c("UPb4","UPb5","UPb6","UPb7","UPb8")) { fmt <- as.integer(substr(f,4,4)); x <- rd(f,method="U-Pb",format=fmt)
  for (cp in c(1,3)) try_({t1 <- age(x,type=1,common.Pb=cp,oerr=1,sigdig=10)
    write.csv(t1,file.path(Sys.getenv("OUT"),paste0("idades_por_grao_",f,"_PbComum",cp,".csv")),row.names=FALSE)
    w <- weightedmean(t1[,c("t.68","err[t.68]")],random.effects=FALSE,detect.outliers=FALSE,plot=FALSE)
    add(f,"Média ponderada 206Pb/238U após correção de Pb comum",ifelse(cp==1,"Pb comum padrão do IsoplotR","Stacey & Kramers 1975"),w$mean["t"],w$mean["s[t]"],w$mswd,w$p.value,nrow(t1))})
}
# Th-Pb, Pb-Pb, Th-U isochrons
for (f in c("ThPb1")) try_({x <- rd(f,method="Th-Pb",format=1); i <- isochron(x,plot=FALSE,oerr=1,sigdig=10)
  add(f,"Isócrona Th-Pb","modelo 1 (York)",i$age["t"],i$age["s[t]"],i$mswd,i$p.value,length(x$x[,1]))})
for (f in c("PbPb1")) try_({x <- rd(f,method="Pb-Pb",format=1); i <- isochron(x,plot=FALSE,oerr=1,sigdig=10)
  add(f,"Isócrona Pb-Pb","modelo 1 (York)",i$age["t"],i$age["s[t]"],i$mswd,i$p.value,length(x$x[,1]))})
for (f in c("ThU1","ThU3")) try_({fmt <- as.integer(substr(f,4,4)); x <- rd(f,method="Th-U",format=fmt); i <- isochron(x,plot=FALSE,oerr=1,sigdig=10)
  add(f,"Isócrona 230Th-238U","modelo 1",i$age["t"],i$age["s[t]"],i$mswd,i$p.value,length(x$x[,1]))})
# Detrital
try_({dz <- read.data(file.path(inst,"inst_DZ.csv"),method="detritals")
  D <- diss(dz,method="KS"); write.csv(as.matrix(D),file.path(Sys.getenv("OUT"),"DZ_distancias_KS.csv"))
  m <- mds(dz,plot=FALSE); write.csv(m$points,file.path(Sys.getenv("OUT"),"DZ_MDS_coordenadas.csv"))
  for (s in names(dz)) add("DZ",paste("Grão mais jovem, amostra",s),"sem erros no arquivo",min(dz[[s]]),n=length(dz[[s]]))})
res <- do.call(rbind,rows); write.csv(res,file.path(Sys.getenv("OUT"),"resultados_referencia_IsoplotR.csv"),row.names=FALSE,fileEncoding="UTF-8")
print(res[,1:8])
