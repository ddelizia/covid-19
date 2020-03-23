import pandas as pd
import numpy as np
from expiringdict import ExpiringDict

cache = ExpiringDict(max_len=100, max_age_seconds=86400/2)


def _normalize_data(dataset_url):
    df = pd.read_csv(dataset_url)
    df_ca = df.set_index('CCAA').drop(['cod_ine'], axis='columns').transpose()
    df_ca.index = pd.to_datetime(df_ca.index, format='%d/%m/%Y')
    return df_ca.reindex(pd.date_range(df_ca.index[0], df_ca.index[-1]))


def all_data():
    if cache.get('data') is None:
        df_cases = _normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_casos.csv')
        df_uci = _normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_uci.csv')
        df_deaths = _normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_fallecidos.csv')
        df_recovered = _normalize_data('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_altas.csv')

        cache['data'] = df_cases, df_uci, df_deaths, df_recovered
    return cache['data']


def get_ccaa():
    df_cases, df_uci, df_deaths, df_recovered = all_data()
    return df_cases.columns


def data_ccaa(ca):
    if cache.get(f'data{ca}') is None:
        df_cases, df_uci, df_deaths, df_recovered = all_data()
        data = pd.concat([df_cases[ca], df_deaths[ca], df_uci[ca], df_recovered[ca]], axis='columns').fillna(method='ffill').fillna(0)
        data.columns = ["all", "deaths", "uci", "recovered"]
        data['remaining'] = data["all"] - data["deaths"] - data["uci"] - data["recovered"]
        cache[f'data{ca}'] = data
    return cache[f'data{ca}']


def data_exp():
    df_cases, df_uci, df_deaths, df_recovered = all_data()
    x = np.linspace(0, df_cases.shape[0] - 1, df_cases.shape[0])
    return np.power(2, x), np.power(2, x/2), np.power(2, x/3), np.power(2, x/4)