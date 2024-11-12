from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import Job,JobBookmark
from .serializers import JobSerializer,JobBookmarkSerializer
from django.db.models import Q, Value, BooleanField
from django.db.models.functions import Coalesce
from django.db.models import CharField, TextField
from django.db.models import Count

class SearchKeyWordView(APIView):

    def get(self, request):

        q = request.query_params.get('q', None)
        pay_from = request.query_params.get('pay_from', None)
        pay_to = request.query_params.get('pay_to', None)
        pay_type = request.query_params.get('pay_type', 'annually')
        job_type = request.query_params.get('job_type', None)
        industry = request.query_params.get('industry', None)

        try:
            #filter from all CharField and TextField
            query = Q()
            if q:
                for field in Job._meta.fields:
                    if isinstance(field, (CharField, TextField)):  
                        query |= Q(**{f"{field.name}__icontains": q})
            
            if pay_from or pay_to:
                conversion_factors = {
                    'annually': 1,
                    'monthly': 12,
                    'daily': 365,
                    'hourly': 365 * 8,
                }
                factor = conversion_factors.get(pay_type, 1)

                if pay_from is not None:
                    query &= Q(salary_min__gte=int(pay_from) * factor)
                if pay_to is not None:
                    query &= Q(salary_max__lte=int(pay_to) * factor)

            if job_type:
                job_type_map = {
                    '1': 'Perm',
                    '2': 'Temp',
                    '3': 'Contract'
                }
                job_types = []
                for jt in job_type.split(','):
                    if jt in job_type_map:      
                        mapped_type = job_type_map[jt]
                        job_types.append(mapped_type)
                if job_types:
                    query &= Q(job_type__in=job_types)
            
            if industry:
                industryList = []
                for i in industry.split(','):
                    industryList.append(i)
                query &= Q(industry__in=industryList)

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
            matching_jobs = Job.objects.filter(query)

            job_type_cal = matching_jobs.values('job_type').annotate(count=Count('job_type'))

            job_type_count = { 'Perm': 0, 'Temp': 0, 'Contract': 0 }
            for item in job_type_cal:
                job_type = item['job_type']
                count = item['count']
                job_type_count[job_type] += count
            
            industry_cal = matching_jobs.values('industry').annotate(count=Count('industry'))

            # industry_count = {}
            # for item in industry_cal:
            #     industry = item['industry']
            #     count = item['count']
            #     industry_count[industry] += count

            if q:
                matching_jobs = matching_jobs.annotate(
                is_in_title=Coalesce(Q(title__icontains=q), Value(False), output_field=BooleanField())
            ).order_by('-is_in_title')
    
            matching_jobs = matching_jobs.order_by('-posted_date').distinct()[offset:limit]
            
            if not matching_jobs.exists():
                return Response({"message": "No jobs found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = JobSerializer(matching_jobs, fields=['id', 'title', 'city', 'salary_min', 'salary_max'] ,many=True)

            return Response({
                "start_result": start_result,
                "end_result": end_result,
                "total_jobs_count": total_jobs_count,
                "job_type_count":job_type_count,
                "industry_count":industry_cal,
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
        

class FetchSaveJobListView(APIView):

    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"message": "user id is missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            jobList = JobBookmark.objects.filter(user_id=user_id)
            
            if not jobList:
                return Response({'message': 'no saved job'},status=status.HTTP_404_NOT_FOUND)
 

            serializer = JobBookmarkSerializer(jobList, many=True)

            return Response({
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"Error: {e}")
            return Response({"message": "Internal server error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)