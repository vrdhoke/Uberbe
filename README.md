# Uberbe

# Summary
1. This ia a Backend Python Flask application for UberBus. 
2. In this application we have designed two pages one for Customer booking and another page is to view the list of bookings made. 
3. We have used Atlas Mongo as a Database to store the list of bookings. 
4. For frontend we have used react. 
5. We are running frontend application on Nginx server and backend on Gunicorn.
6. The whole application is deployed on AWS using Terraform Provisioning.

# How to Run
1. This application is automated using terraform provisioning, hence downloading of dependencies has been handled.
2. Run the terraform script, first do Terraform init
3. Run terrafrom plan
4. Run terraform apply
5. Associate the created elastic IP with the newly created instance on AWS
6. Open the Elastic IP on browser to view the application.
