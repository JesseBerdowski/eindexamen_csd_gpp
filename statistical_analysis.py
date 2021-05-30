# native python imports
import random
# local imports
from data_preparation import csv_to_dataframe
# third party imports
from pandas import DataFrame, concat
from numpy import ones_like, std, asarray, sort, arange, interp
from matplotlib.pyplot import figure, savefig, legend, grid
from scipy.stats import ttest_1samp
from sklearn.linear_model import LinearRegression


class Analysis:
    def __init__(self, hparams, data_log, r_file):
        self.hparams = hparams
        self.data_log = data_log
        self.df = csv_to_dataframe(r_file, datalog=data_log)

    def _create_clusters(self, df, keys=list()):
        # create clusters from key
        clusters = list(self._cluster_on_keys(keys[0], df))

        # yield clusters of treatments within a venue cluster
        for c in clusters:
            yield list(self._cluster_on_keys(keys[1], c))

    def _cluster_on_keys(self, c_key, df=None):
        if not isinstance(df, DataFrame):
            df = self.df

        def cluster_data(val):
            for index, row in df.iterrows():
                if row[c_key] == val:
                    yield row

        if c_key == 'venue':
            venues_lst = [i for i in range(self.hparams.no_rests)]
            for venue in venues_lst:
                yield DataFrame(cluster_data(venue))

        elif c_key == 'treatment':
            treat_lst = self.hparams.treatments
            for treat in treat_lst:
                yield DataFrame(cluster_data(treat))

    @staticmethod
    def _regression(values):
        # the y value is the correct values per treatment
        y = values

        # X = 1, see Equation (1)
        X = ones_like(y).reshape(-1, 1)

        # linear regression
        reg = LinearRegression().fit(X, y)
        coeff = float(reg.predict([[1]]))

        return coeff

    @staticmethod
    def _calc_mean(lst):
        return sum(lst) / len(lst)

    @staticmethod
    def _means_to_ses(means):
        return std(means)


class Bootstrapping(Analysis):
    def __init__(self, hparams, data_log, r_file):
        """
        calculates standard error by resampling using bootstrapping w/ replacement over clusters where each venue
        contributes to a cluster, and calculates p_value by running t-test over the standard errors
        """
        super().__init__(hparams, data_log, r_file)

    @staticmethod
    def _bootstrap_resample(pool):
        resample = random.choices(pool, k=len(pool))

    @staticmethod
    def _create_pool(c):
        for val in c['values']:
            yield val

    def _n_regressions(self, pool):
        for n in range(self.hparams.bootstrap_n):
            # bootstrap w/ replacement
            resample = random.choices(pool, k=len(pool))
            # calculate coefficient
            yield self._regression(values=resample)

    def _resample_coeff_per_treatment(self, v_cs):
        t_pool = []
        mean_coeffs = []
        for v_c in v_cs:
            treatment = v_c.iloc[1,2]
            # create pool from values venue_cluster
            pool = list(self._create_pool(v_c))

            # create `t_pool` containing all different
            t_pool += pool
            coeffs = list(self._n_regressions(pool))
            mean_coeffs.append(self._calc_mean(coeffs))

        return mean_coeffs, t_pool, treatment

    @staticmethod
    def _calc_p_val(ses, mu):

        # mu is is covariance of the total sample population, null hypothesis is 'how big are the chances that the
        # coefficient of the individual clusters is randomly sampled from the total covariance'
        p_val = ttest_1samp(ses, mu)
        return 1 - p_val.pvalue

    def _return_stats(self, resampled_coeffs, pool, treatment):
        # calculate standard error for the mean coeffs
        print('res coef: {}'.format(resampled_coeffs))
        se = self._means_to_ses(resampled_coeffs)
        resampled_coeff = self._calc_mean(resampled_coeffs)
        pool_coeff = self._regression(pool)
        p_val = self._calc_p_val(resampled_coeffs, pool_coeff)
        return {'treatment': treatment, 'standard_error': round(se, 3),
                'coeff': round(resampled_coeff, 3), 'p_value': round(p_val, 3)}

    def _results_of_treatments(self, t_clusters):
        # iterate over the treatment clusters
        for v_in_t_clusters in t_clusters:

            # return resampled coeffs per treatment
            resampled_coeffs, pool, treatment = self._resample_coeff_per_treatment(v_in_t_clusters)
            yield self._return_stats(resampled_coeffs, pool, treatment)

    def analyze(self):
        # create clusters of venues per treatment
        t_clusters = self._create_clusters(self.df, keys=['treatment', 'venue'])  # checked
        return list(self._results_of_treatments(t_clusters))


class PlaceboTreatment(Analysis):
    def __init__(self, hparams, data_log, r_file):
        """

        calculates CDF for placebo treatment w/ non-parametric permutation test, see Figure 4
        """
        super().__init__(hparams, data_log, r_file)
        self.cs = list(self._create_clusters(df=None, keys=['venue', 'treatment']))

    def _randomize_treatment(self):
        # duplicate object to keep original intact
        rand_treat_cs = list(self.cs)

        # iterate over restaurants
        for treatment_cluster in rand_treat_cs:
            # list of the treatments
            treatments = self.hparams.treatments
            # randomly shuffle treatments
            random.shuffle(treatments)

            # iterate over clusters and randomized treatments:
            for i, cluster in enumerate(treatment_cluster):
                cluster['treatment'] = treatments[i]

        ven_cs = []
        # remove 1dim clusters, type(cluster) = pd.Dataframe
        for ven_c in rand_treat_cs:
            ven_cs.append(concat(ven_c))

        # create single cluster
        single_cluster = concat(ven_cs)

        # create clusters w/ randomized treatment, clustered on treatment
        return self._create_clusters(df=single_cluster, keys=['treatment', 'venue'])

    def clustered_regression(self, rand_treat_cs):
        """perform regression per treatment"""

        for rand_treat_c in rand_treat_cs:
            for r_treat in rand_treat_c:
                yield self._regression(asarray(r_treat['values']))

    def _iterate_placebo_treats(self):
        def iterate():
            for n in range(self.hparams.placebo_n):
                rand_treat_cs = list(self._randomize_treatment())
                yield list(self.clustered_regression(rand_treat_cs))

                if n % 5 == 0:
                    print('completed {} iterations...'.format(n + 1))

                print('completed {} iterations...'.format(n + 1))

        placebo_iterations = iterate()
        single_cluster_placebo = []

        # all clusters to a single list
        for cluster in placebo_iterations:
            for c in cluster:
                single_cluster_placebo.append(c)

        single_cluster_placebo = asarray(single_cluster_placebo)
        return sort(single_cluster_placebo)

    @staticmethod
    def _visualize_cdf(sorted_coeffs, results=None):
        """https://stackoverflow.com/questions/24788200/calculate-the-cumulative-distribution-function-cdf-in-python"""

        p = 1. * arange(len(sorted_coeffs)) / (len(sorted_coeffs) - 1)

        fig = figure()
        fig = figure()

        ax = fig.add_subplot(111)
        ax.plot(sorted_coeffs, p, c='w')
        ax.set_xlabel('$coeff$')
        ax.set_ylabel('$p$')
        ax.set_facecolor('lightskyblue')
        # colors = ['b', 'g', 'r', 'c']
        coeff_dicts =[]
        for result in results:
            p_val_coeff = interp(result['coeff'], sorted_coeffs, p)
            coeff_dict ={'p_value_plac': p_val_coeff, 'coeff': result['coeff'], 'treatment': result['treatment']}

            coeff_dicts.append(coeff_dict)
            ax.vlines(x=result['coeff'], ymin=0, ymax=1,
                      label='treatment {} w/ p_val {}'.format(result['treatment'], round(p_val_coeff, 2 )))

        legend(loc='lower right')
        grid(':')
        savefig(fname='static/out_visualisations/placebo_cdf')
        return coeff_dicts

    def analyze(self, visualize_data=True, p_vals=None):
        sorted_coeffs = self._iterate_placebo_treats()

        if visualize_data:
            return self._visualize_cdf(sorted_coeffs, p_vals)


