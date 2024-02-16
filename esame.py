#Creo l'eccezione da alzare come da istruzioni
class ExamException(Exception):
    pass

class CSVTimeSeriesFile:

    def __init__(self, name):
            self.name = name


    def get_data(self):
        #Creo la lista time_series e una variabile che mi servirà poi per controllare
        #ed alzare l'errore in caso Timestamp
        time_series = []
        data_precedente = None
                
        try:
            with open(self.name, 'r') as my_file:
                #apro il file con with in modo tale che mi si chiuda poi da solo
                #faccio scorrere tramite readline l'intestazione delle colonne
                #(date, passengers) che si trova alla prima riga
                my_file.readline()

                #qui inizio a leggere dalla seconda riga in poi
                #splittando le varie righe 
                for linea in my_file:
                    riga = linea.strip().split(',')
                                        
                    #ignoro le righe con meno di due elementi 
                    if len(riga) < 2:
                        continue
                                                
                    try: 
                        date = riga[0]
                        passeggeri = int(riga[1])

                        #controllo validità delle date 
                        controllo_data = date.split('-')
                        anno = int(controllo_data[1])
                        mese = int(controllo_data[2])
                        if anno > 9999 or anno < 1000 or mese <= 0 or mese >12:
                            continue
                                                        
                        #controllo che il valore non sia negativo
                        if passeggeri < 0:
                            continue
                                                        
                        #qui controllo le date se sono fuori ordine o duplicate
                        # e nel caso interrompò l'esecuzione
                        if data_precedente is not None and date < data_precedente:
                            raise ExamException("Timestamp è fuori ordine")
                                                        
                        if data_precedente is not None and date == data_precedente:
                            raise ExamException("Timestamp duplicato")

                        #se passa i controllo invio 
                        time_series.append([date, passeggeri])
                    
                        #setto la data attaule per riprocedere al controllo nelle prossime righe 
                        data_precedente = date
                                                
                        #se incontro segli errori nella conversione ad intero skippo la riga    
                    except ValueError:
                        continue
                                                
        #Fermo il programma nel caso non sia possibile lavorare nel file                
        except FileNotFoundError as e:
            raise ExamException("Non è possibile lavorare sul file") from e
        return time_series


def compute_increments(time_series, first_year, last_year):
    #necessito di sapere se gli anni inseriti sono validi

    #inizio a vedere se sono interi
    try:
        first_year = int(first_year)
        last_year = int(last_year)
    except ValueError as e:
        raise ExamException(
            "Gli estremi dell intervallo devono essere numeri interi") from e

    #mi assicuro che siano delle date "reali"
    if first_year < 1900 or first_year > 2500:
        raise ExamException("Il primo anno inserito è una data non valida")
    if last_year < 1900 or last_year > 2500:
        raise ExamException("Il secondo anno inserito è una data non valida")

    #posso inziare a creare il calcolatore per le variazioni
    try:
        #prima cosa creo il dizionario degli incrementi
        incrementi = {}
        #avrò bisogno di un dizionario di appoggio in cui metterò il conteggio dei
        #passeggeri per ogni anno 
        pass_conteggio = {}

        #inzio a ciclare e lo faccio per tutti gli anni
        for date, passeggeri in time_series:
            #qui ho utilizzato una libreria di python per velocizzare il lavoro
            anno = date.year
            #controllo che l'anno in cui sto ciclando sia all'interno delle date in input
            if first_year <= anno <= last_year:
                
                #se l'anno in cui sto ciclando non è ancora presente nel dizionario
                #lo aggiungo come chiave e metto i passeggeri 
                if anno not in pass_conteggio:
                    pass_conteggio[anno] = [passeggeri]
                #altrimenti se già presente aggiungo al dizionario di quell anno
                #il dato relativo ai passeggeri
                else:
                    pass_conteggio[anno].append(passeggeri)

        #nel caso le due date siano consecutive e uno dei due anni non sia presente nel
        #dizionario torno una lista vuota
        if last_year - first_year == 1 and (first_year not in pass_conteggio or 
                                            last_year not in pass_conteggio):
            return []

        #ora valuto se ci sono i dati necessari per il calcolo degli anni consecutivi

        #itero nel ciclo cercando nell'anno successivo a quello di partenza
        #fino all'ultimo incluso
        for anno in range(first_year + 1, last_year + 1):
            #verifico che ci sia il conteggio dei passeggeri per l'anno corrente
            #e per quello precedente
            if anno not in pass_conteggio or anno - 1 not in pass_conteggio:
                continue
                #nel caso non ci sia salto quell'anno senza interrompere il codice

            
            #calcolo la variazione degli incrementi medi dell'anno corrente
            avg_pass_corrente = sum(pass_conteggio[anno]) / len(pass_conteggio
                                                                        [anno])
            #calcolo la variazione degli incrementi medi dell'anno precedente
            avg_pass_preced = sum(pass_conteggio[anno - 1]) / len(pass_conteggio
                                                                        [anno - 1])
            #aggiungo le variazione degli incrementi medi
            #dei vari anni nel dizionario mettendo le opportune chiavi
            incrementi[f"{anno - 1}-{anno}"] = avg_pass_corrente - avg_pass_preced
            
         #usciti dal ciclo ritorno i dizionari 
        return incrementi
    #nel caso di errore di calcolo nel try alzo un eccezione
    except Exception as e:
            raise ExamException(f"Errore durante il calcolo degli incrementi: {e}") from e


