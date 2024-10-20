import json
with open('test.json', 'r') as file:
        data = json.load(file)

        specific_currencies = "UAH"
        bb={}
        aa={}
        '''for date in data['rates'].keys():
            for currency, rate in data['rates'][date].items() :
                if currency == specific_currencies:
                    aa[currency] = rate
            bb[date] = aa '''
        for date in data['rates'].keys():
            filtered_rates = {currency: rate for currency, rate in data['rates'][date].items() if currency == specific_currencies}
            aa[date] = filtered_rates
                
                


            
        '''dates = [date for date in data['rates'].values()]
        for date in dates :
            filtered_rates = {currency: rate for currency, rate in data['rates'][date].items() if currency == specific_currencies}
            filtered_rates = {currency: rate for currency, rate in data['rates']['2019-01-01'].items() if currency == specific_currencies}'''
        
        print(filtered_rates)
        print(aa)
        for date, value in aa.items() :
            for currency, rate in value.items() :
                print(f"Date : {date} Currency : {currency} Rate : {rate}")
              
        print(type(data['rates'][date].items()))