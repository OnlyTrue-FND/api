import datetime
import random
import re
import statistics
from collections import Counter
from urllib.parse import urlparse, parse_qs

import requests
import tldextract
from bs4 import BeautifulSoup
from django.db import models
from django.db.models import Avg
from django.utils import timezone
from goose3 import Goose
from nltk.tokenize import RegexpTokenizer


class WebPage(models.Model):
    CURRENT_SCORES_VERSION = 3

    url = models.URLField(unique=True)
    content_score = models.PositiveIntegerField(blank=True, null=True)
    base_domain = models.CharField(max_length=250)
    scores_version = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def site_score(self):
        return (WebPage.objects
                .filter(base_domain=self.base_domain)
                .aggregate(site_score=Avg('content_score'))
                )['site_score']

    @property
    def global_score(self):
        exclude = ['global_score', 'compute_scores']
        fields = list(filter(lambda x: "_score" in x and x not in exclude, dir(self)))
        scores = list(map(lambda x: getattr(self, x), fields))
        return statistics.mean(scores)

    def compute_scores(self):
        original_url = self.url
        parsed_uri = urlparse(original_url)

        # Extract the title and the text of the article
        g = Goose()
        article = g.extract(url=original_url)
        title = article.title

        print("1")
        tokenizer = RegexpTokenizer(r'\w+')
        print("2")
        tokens = tokenizer.tokenize(article.cleaned_text)
        print("3")
        non_punct = re.compile('.*[A-Za-z0-9].*')
        print("4")
        filtered = [w for w in tokens if non_punct.match(w)]
        print("5")
        counts = Counter(filtered)
        print("6")
        print(counts)

        # Construct the url for the GET request
        title = str(title.replace(" ", "-"))
        low_date = ((article.publish_datetime_utc - datetime.timedelta(days=7)).date())
        high_date = ((article.publish_datetime_utc + datetime.timedelta(days=7)).date())

        new_low_date = low_date.strftime('%m/%d/%Y')
        new_high_date = high_date.strftime('%m/%d/%Y')

        url_request = f"https://www.google.fr/search?q={title}&tbs=cdr:1,cd_min:{new_low_date},cd_max:{new_high_date}"
        print("URL constructed")
        print("URL : {}".format(url_request))

        print("Execute the request")
        # GET request
        page = requests.get(url_request)
        soup = BeautifulSoup(page.content, "lxml")
        for link in soup.find_all("a", href=re.compile("(?<=/url)([?&])q=(htt.*://.*)")):
            linked_url = parse_qs(urlparse(link['href']).query)['q'][0]

            if "webcache" not in linked_url and parsed_uri.netloc not in linked_url:
                article = g.extract(url=linked_url)
                print("Name of the article:", article.title)
                print("Pubication date:", article.publish_datetime_utc)
                print("Article content:\n", article.cleaned_text)
                print("URL of the article:", linked_url)
                print()

        # TODO
        self.content_score = random.randint(0, 100)

        self.scores_version = WebPage.CURRENT_SCORES_VERSION

        tld_extract = tldextract.TLDExtract(
            cache_file='api/external_data/public_suffixes_list.dat',
            include_psl_private_domains=True
        )
        url_extraction = tld_extract(self.url)
        base_domain = f"{url_extraction.domain}.{url_extraction.suffix}".lower()
        print(base_domain)
        self.base_domain = base_domain

        self.save()
        return self

    def to_dict(self):
        fields_to_serialize = ['url', 'global_score']
        self_serialized = {field: getattr(self, field) for field in fields_to_serialize}
        scores = ['content_score', 'site_score']
        self_serialized['scores'] = {field: getattr(self, field) for field in scores}

        return self_serialized

    @classmethod
    def from_url(cls, url):
        existing = cls.objects.filter(url=url).first()

        if (existing
                and existing.scores_version == WebPage.CURRENT_SCORES_VERSION
                and existing.updated_at > timezone.now() - datetime.timedelta(days=7)):
            return existing

        elif not existing:
            existing = cls(url=url, scores_version=WebPage.CURRENT_SCORES_VERSION)

        return existing.compute_scores()

    def __str__(self):
        return self.url
