# Importing Libraries
import argparse
import logging
import multiprocessing as mp
import os
import pandas as pd
import PyPDF2
import re
import requests
import sys
import urllib.request
import utils

from bs4 import BeautifulSoup
import datetime
from opensearchpy import OpenSearch
from time import sleep, time
from tqdm import tqdm

''' Set the maximum depth of the Python interpreter stack to 100000. 
This limit prevents infinite recursion from causing an overflow of the C stack and crashing Python.'''
sys.setrecursionlimit(100000)