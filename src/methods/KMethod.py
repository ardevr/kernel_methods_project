from src.tools.utils import Logger, Parameters, Timer
import numpy as np
from src.tools.utils import Score


class KMethodCreate(type):
    def __init__(cls, clsname, superclasses, attributedict):
        def init(self, kernel=None, parameters=None, verbose=True):
            super(cls, self).__init__(
                kernel=kernel,
                name=clsname,
                parameters=parameters,
                verbose=verbose,
                cls=cls)

        cls.__init__ = init


def klogger(name, pca=False, wkrr=False):
    def wrap(fitfunc):
        def f(self, dataset=None, labels=None, K=None, w=None):
            t = Timer()
            self._log("Fitting {}..".format(name))
            Logger.indent()
            t.start()

            if K is None:
                self.load_dataset(dataset, labels)
                if pca:
                    K = self.kernel.KC
                else:
                    K = self.kernel.K

            if wkrr:
                result = fitfunc(self, K, w)
            else:
                result = fitfunc(self, K)

            t.stop()
            Logger.dindent()
            self._log("Fitting done! (computed in {})\n".format(t))

            return result

        return f

    return wrap


class KMethod(Logger):
    def __init__(self,
                 kernel,
                 name="KMethod",
                 parameters=None,
                 verbose=True,
                 cls=None):

        self.verbose = verbose
        self.kernel = kernel

        self.param = Parameters(parameters, cls.defaultParameters)

        self.__name__ = name
        self.verbose = verbose
        self._alpha = None
        self._b = None
        self.kernel = kernel
        self._labels = None

        # For the KPCA
        self._projections = None

    # Load the dataset (if there are one) in the kernel
    # or just load the labels
    def load_dataset(self, dataset=None, labels=None):
        if dataset is None:
            if labels is None:
                self._log("Taking data from the kernel directly")
                self._labels = self.kernel.labels
            else:
                self._labels = labels
        else:
            self._log("Load the data in the kernel")
            self.kernel.dataset = dataset
            self._labels = None  # take the kernel one

    def predict(self, x):
        K_xi = self.kernel.predict(x)
        return self.alpha.dot(K_xi) + self.b

    def predictBin(self, x):
        pred = self.predict(x)
        return 1 if pred > 0 else -1

    def predict_array(self, X, binaire=True, desc="Predictions"):
        if binaire:
            fonc = self.predictBin
        else:
            fonc = self.predict

        results = []
        for i in self.vrange(len(X), desc):
            results.append(fonc(X[i]))
        return np.array(results)

    def score_recall_precision(self, dataset, nsmall=None):
        mask = np.arange(dataset.n)
        np.random.shuffle(mask)
        if nsmall is not None:
            mask = mask[:nsmall]
            stringset = "training set ({} samples)".format(nsmall)
        else:
            stringset = "training set"

        t = Timer()
        t.start()
        predictions = self.predict_array(dataset.data[mask], binaire=True, desc="Computing train set score")
        score = Score(predictions, dataset.labels[mask])
        t.stop()
        self._log("Results of the {} (computed in {})".format(stringset, t))
        Logger.indent()
        self._log(score)
        Logger.dindent()
        self._log("")
        return score

    def sanity_check(self):
        mask = np.arange(self.n)
        np.random.shuffle(mask)

        preds = self.predict_array(
            self.data[mask][:20], binaire=False, desc="Sanity check")

        def form(number):
            return "{0:.2e}".format(number)

        strings = [form(pred) for pred in preds[:5]]

        self._log("Sanity check:")
        Logger.indent()
        self._log("Min: " + form(min(preds)))
        self._log("Max: " + form(max(preds)))
        self._log("Random values:", strings)
        Logger.dindent()

        self._log("")

    @property
    def alpha(self):
        if self._alpha is None:
            raise Exception("Model is not trained yet")
        return self._alpha

    @property
    def b(self):
        if self._b is None:
            return 0
        return self._b

    @property
    def dataset(self):
        return self.kernel.dataset

    @property
    def data(self):
        return self.kernel.data

    @property
    def labels(self):
        if self._labels is None:
            return self.kernel.labels
        return self._labels

    @property
    def n(self):
        return self.kernel.n

    @property
    def m(self):
        return self.kernel.m

    def __str__(self):
        name = "Method: " + self.__name__
        param = "Parameters: " + str(self.param)
        return name + ", " + param

    def __repr__(self):
        return self.__str__()


def AllClassMethods():
    from src.methods.kknn import KKNN
    from src.methods.klr import KLR
    from src.methods.ksvm import KSVM
    from src.methods.simple_mkl import SimpleMKL
    methods = [KKNN, KLR, KSVM, SimpleMKL]
    names = [method.name for method in methods]

    return methods, names
