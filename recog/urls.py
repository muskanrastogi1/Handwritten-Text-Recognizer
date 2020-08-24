from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import handwritingViewSet

router = DefaultRouter()
router.register('upload', handwritingViewSet, basename = 'azureUpload')

urlpatterns = router.urls