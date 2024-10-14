from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Job
from .serializers import JobSerializer
from django.db.models import Q, Value, BooleanField
from django.db.models.functions import Coalesce
from django.db.models import CharField, TextField

class SearchKeyWordView(APIView):

    def get(self, request):
        q = request.query_params.get('q')
        if not q:
            return Response({"message": "keyword is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #filter from all CharField and TextField
            query = Q()
            for field in Job._meta.fields:
                if isinstance(field, (CharField, TextField)):  
                    query |= Q(**{f"{field.name}__icontains": q})

            #order the result: title includes keyword will be in the front 
            matching_jobs = Job.objects.filter(query).annotate(
                is_in_title=Coalesce(Q(title__icontains=q), Value(False), output_field=BooleanField())
            ).order_by('-is_in_title').distinct() 
    
            if not matching_jobs.exists():
                return Response({"message": "No jobs found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = JobSerializer(matching_jobs, many=True)
            

            return Response(serializer.data, status=status.HTTP_200_OK)
            
     
        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)