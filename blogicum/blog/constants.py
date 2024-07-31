from django.urls import reverse_lazy


INDEX_URL = "blog:index"
PROFILE_URL = "blog:profile"
POST_DETAIL_URL = "blog:post_detail"

# Константы URL
INDEX = reverse_lazy(INDEX_URL)
POST_DETAIL = reverse_lazy(POST_DETAIL_URL)

RESTRICTION = 30
PAGINATE = 10
