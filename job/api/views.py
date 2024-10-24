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

        try:
            #filter from all CharField and TextField
            query = Q()
            for field in Job._meta.fields:
                if isinstance(field, (CharField, TextField)):  
                    query |= Q(**{f"{field.name}__icontains": q})

            # Pagination parameters: page number and page size
            page_size = 10  
            page = int(request.query_params.get('page', 1))  

            # Calculate offset and limit for the query
            offset = (page - 1) * page_size
            limit = offset + page_size

            # Total number of matching jobs
            total_jobs_count = Job.objects.filter(query).count()

            # Calculate result range (e.g., "Showing results 1 - 10 out of 90")
            start_result = 1
            end_result = min(limit, total_jobs_count)

            #order the result: title includes keyword will be in the front 
            matching_jobs = Job.objects.filter(query).annotate(
                is_in_title=Coalesce(Q(title__icontains=q), Value(False), output_field=BooleanField())
            ).order_by('-is_in_title', '-posted_date').distinct()[offset:limit]
    
            if not matching_jobs.exists():
                return Response({"message": "No jobs found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = JobSerializer(matching_jobs, fields=['id', 'title', 'city', 'salary_min', 'salary_max'] ,many=True)
            

            return Response({
                "start_result": start_result,
                "end_result": end_result,
                "total_jobs_count": total_jobs_count,
                "results": serializer.data
            }, status=status.HTTP_200_OK)
            
     
        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class FetchSingleJobView(APIView):

    def get(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({"message": "Job id is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            existing_job = Job.objects.get(id=id)

            serializer = JobSerializer(existing_job)

            if not existing_job:
                return Response({'message': 'Invalid job'},status=status.HTTP_404_NOT_FOUND)
            

            return Response({
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
            
     
        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)