from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Prescription
from .serializers import PrescriptionSerializer

# GET all + POST new
class PrescriptionListView(APIView):

    def get(self, request):
        prescriptions = Prescription.objects.all()
        serializer = PrescriptionSerializer(prescriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PrescriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# GET single + DELETE
class PrescriptionDetailView(APIView):

    def get_object(self, pk):
        try:
            return Prescription.objects.get(pk=pk)
        except Prescription.DoesNotExist:
            return None

    def get(self, request, pk):
        prescription = self.get_object(pk)
        if not prescription:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = PrescriptionSerializer(prescription)
        return Response(serializer.data)

    def delete(self, request, pk):
        prescription = self.get_object(pk)
        if not prescription:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        prescription.delete()
        return Response({"success": True, "message": "Prescription deleted"}, status=status.HTTP_200_OK)