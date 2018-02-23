def selectdata(fname,factor,value,posofkey=0):
	f=open(fname,'rb')
	g=open('key_of_'+value,'wb')
	attribute = f.readline().split()
	pos=attribute.index(factor)
	line = f.readline()
	counter=0
	while line:
		tem=line.split()
		if tem[pos]==value:
			g.write(tem[posofkey]+'\n')
			counter += 1
		line=f.readline()
	f.close()
	g.close()
	print str(counter)+' lines of data is selected'

def matchdata(inname,key,kname,outname):
	f=open(inname,'rb')
	o=open(outname,'wb')
	k=open(kname,'rb')
	l=open('lose_'+outname,'wb')
	k.seek(0)
	attribute = f.readline()
	o.write(attribute)
	pos=attribute.split().index(key)
	
	kline=k.readline().replace('\n','')
	fline=f.readline()
	tem=fline.split()
	matchcounter=0
	misscounter=0
	while(kline):
		if(tem):
			if(int(tem[pos].replace('tt',''))<int(kline.replace('tt',''))):
				fline=f.readline()
				tem=fline.split()
			elif(int(tem[pos].replace('tt',''))==int(kline.replace('tt',''))):	
			#o.write(fline)
			#fline=f.readline()
			#tem=fline.split()
						
				while(tem[pos]==kline):
					o.write(fline)
					matchcounter+=1
					fline=f.readline()
					tem=fline.split()
					if not fline:
						break
				kline=k.readline().replace('\n','')
			else:#int(tem[pos])>int(kline)
				l.write(kline+'\n')
				misscounter +=1
				kline=k.readline().replace('\n','')
		else:
			l.write(kline+'\n')
			misscounter +=1
			kline=k.readline().replace('\n','')
	f.close()
	o.close()
	k.close()	
	l.close()
	print inname+' match finished'+'. '+str(matchcounter)+' data matched'+'. '+str(misscounter)+' data lost'

def cleandata():
	selectdata('title.basics.tsv','titleType','movie',posofkey=0)
	matchdata('title.crew.tsv','tconst','key_of_movie','title_cleaned.crew.tsv')
	matchdata('title.principals.tsv','tconst','key_of_movie','title_cleaned.principals.tsv')
	matchdata('title.ratings.tsv','tconst','key_of_movie','title_cleaned.ratings.tsv')
	matchdata('title.akas.tsv','titleId','key_of_movie','title_cleaned.akas.tsv')
