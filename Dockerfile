FROM amazonlinux:2.0.20210126.0
WORKDIR /app
COPY requirements.txt requirements.txt
RUN yum update -y
RUN amazon-linux-extras install python3.8
RUN yum install -y \
python3-pip \
zip \
RUN yum install git -y
RUN yum -y clean all
RUN python3.8 -m pip install --upgrade pip
RUN mkdir layer_dir
RUN cd layer_dir
RUN mkdir python.
RUN pip3 install -r requirements.txt -t /layer_dir/python