import os

import dash_html_components as html
import numpy as np
import pandas as pd
from expiringdict import ExpiringDict
from scipy.optimize import curve_fit

cache = ExpiringDict(max_len=100, max_age_seconds=120)


class Data:

    def build_data(self):
        pass

    def dash_title(self):
        pass

    def dash_data_ref(self):
        pass

    def all_data(self):
        if cache.get('data') is None:
            cache['data'] = self.build_data()
        return cache['data']

    def get_ccaa(self):
        df_cases, df_uci, df_deaths, df_recovered = self.all_data()
        return df_cases.columns

    def data_ccaa(self, ca):
        if cache.get(f'data{ca}') is None:
            df_cases, df_uci, df_deaths, df_recovered = self.all_data()
            data = pd.concat([df_cases[ca], df_deaths[ca], df_uci[ca], df_recovered[ca]], axis='columns').fillna(method='ffill').fillna(0)
            data.columns = ["all", "deaths", "uci", "recovered"]
            data['remaining'] = data["all"] - data["deaths"] - data["uci"] - data["recovered"]
            cache[f'data{ca}'] = data
        return cache[f'data{ca}']

    def lin_space(self):
        df_cases, df_uci, df_deaths, df_recovered = self.all_data()
        x = np.linspace(0, df_cases.shape[0] - 1, df_cases.shape[0])
        return x

    def data_exp(self):
        x = self.lin_space()
        return np.power(2, x), np.power(2, x/2), np.power(2, x/3), np.power(2, x/4)

    def exponential_func(self, x, a, b):
        return a*np.exp(-b*x)

    def exp_fit(self, y, ca):
        if cache.get(f'exp{ca}') is None:
            x = self.lin_space()
            popt, pcov = curve_fit(self.exponential_func, x[:-5], y[:-5], p0=(1, 1e-6))
            cache[f'exp{ca}'] = self.exponential_func(x, *popt)

        return cache[f'exp{ca}']


class DataEs(Data):

    def _normalize_data(self, dataset_url):
        df = pd.read_csv(dataset_url)
        df_ca = df.set_index('CCAA').drop(['cod_ine'], axis='columns').transpose()
        df_ca.index = pd.to_datetime(df_ca.index, format='%Y/%m/%d')
        return df_ca.reindex(pd.date_range(df_ca.index[0], df_ca.index[-1]))

    def build_data(self):
        df_cases = self._normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_casos.csv')
        df_uci = self._normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_uci.csv')
        df_deaths = self._normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_fallecidos.csv')
        df_recovered = self._normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_altas.csv')

        return df_cases, df_uci, df_deaths, df_recovered

    def dash_title(self):
        return 'Covid-19 Spain Dashboard'

    def dash_data_ref(self):
        return html.P(children=[
            html.Strong(children=self.dash_title()),
            ' by ',
            html.A(href='https://github.com/ddelizia', children='Danilo Delizia'),
            '. The source code is licensed under ',
            html.A(href='http://opensource.org/licenses/mit-license.php', children='MIT'),
            '. Data from ',
            html.A(href='https://github.com/datadista/datasets/tree/master/COVID%2019', children='Github datadista/datasets'),
        ])


class DataIt(Data):

    def build_data(self):
        df = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/dpc-covid19-ita-regioni.csv')
        df['data'] = pd.to_datetime(df['data'])
        df['date'] = df['data']
        df.set_index(['data', 'codice_regione'], inplace=True)
        df_cases = pd.DataFrame()
        df_deaths = pd.DataFrame()
        df_uci = pd.DataFrame()
        df_recovered = pd.DataFrame()
        df_tests = pd.DataFrame()
        for region in df['denominazione_regione'].unique():
            df_cases[region] = df[df['denominazione_regione'] == region].set_index('date')['totale_casi']
            df_cases.rename(columns={'totale_casi': region}, inplace=True)

            df_deaths[region] = df[df['denominazione_regione'] == region].set_index('date')['deceduti']
            df_deaths.rename(columns={'deceduti': region}, inplace=True)

            df_uci[region] = df[df['denominazione_regione'] == region].set_index('date')['terapia_intensiva']
            df_uci.rename(columns={'terapia_intensiva': region}, inplace=True)

            df_recovered[region] = df[df['denominazione_regione'] == region].set_index('date')['dimessi_guariti']
            df_recovered.rename(columns={'dimessi_guariti': region}, inplace=True)

            df_tests[region] = df[df['denominazione_regione'] == region].set_index('date')['tamponi']
            df_tests.rename(columns={'tamponi': region}, inplace=True)

        df_cases['Total'] = df_cases.sum(axis=1)
        df_deaths['Total'] = df_deaths.sum(axis=1)
        df_uci['Total'] = df_uci.sum(axis=1)
        df_recovered['Total'] = df_recovered.sum(axis=1)
        df_tests['Total'] = df_tests.sum(axis=1)
        return df_cases, df_uci, df_deaths, df_recovered

    def dash_title(self):
        return 'Covid-19 Italy Dashboard'

    def dash_data_ref(self):
        return html.P(children=[
            html.Strong(children=self.dash_title()),
            ' by ',
            html.A(href='https://github.com/ddelizia', children='Danilo Delizia'),
            '. The source code is licensed under ',
            html.A(href='http://opensource.org/licenses/mit-license.php', children='MIT'),
            '. Data from ',
            html.A(href='https://github.com/pcm-dpc/COVID-19', children='Github pcm-dpc/COVID-19'),
        ])


COUNTRY = os.getenv('COUNTRY')
COUNTRY_MAPPING = {
    'IT': DataIt(),
    'ES': DataEs(),
}


def getData():
    if COUNTRY is None:
        return COUNTRY_MAPPING['ES']
    return COUNTRY_MAPPING[COUNTRY]