import datetime
import boto3
from notes.models import Data


class UploadImage:

    def smd_response(self, success, message, data):
        response = {"success": "", "message": "", "data": "", 'success': success, 'message': message, 'data': data}
        print("inside response")
        return response

    def upload_file(self, image):
        s3 = boto3.resource('s3')
        resp=s3.meta.client.upload_fileobj(image, "neweast", "file")             # clint upload to aws
        bucket_location = boto3.client('s3').get_bucket_location(Bucket='neweast')
        object_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format( bucket_location['LocationConstraint'], 'neweast', 'file')
        print(object_url)
        now = datetime.datetime.now()
        storeobj = Data(path=object_url, datetime=now,filename=image)
        storeobj.save()
        response = self.smd_response(True, 'data successfuly stored in db', '')                       # getting back response
        return response