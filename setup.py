from setuptools import setup, find_packages
import rpml

setup(
    name='rpml',
    version='1.0',
    description='Modelo predictivo para etiquetas de mensajes de RapidPro',
    url='https://github.com/opintel/mi-salud',
    author='Jose Antonio Sanchez',
    author_email='j.sanchez@opianalytics.com',
    keywords='ml, rapidpro',
    install_requires=[
        'nltk==3.2.4',
        'scikit-learn==0.19.2',
        'sklearn==0.0',
        'numpy==1.13.3',
        'scipy==1.1.0',
        'xgboost==0.80',
        'Django==2.1',
        'emoji==0.5.0',
        'requests==2.19.1'
    ],
    include_package_data=True,
    packages=find_packages(),
    data_files=[('rpml', [
        'rpml/static/modelo/mat_tfidf.pkl',
        'rpml/static/modelo/modelo.pkl',
        'rpml/static/modelo/pca.pkl',
    ])]
)