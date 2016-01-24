## myPiip
# Description: Update my internal and external RaspberryPi IP using Route53
# Author: Raphael Rabelo (http://github.com/rabeloo)

from boto3.session import Session
import optparse, sys, os, socket, fcntl, struct
import urllib, re
import ConfigParser

def get_local_ip(ifname):
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = socket.inet_ntoa(fcntl.ioctl( s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
    dns_name(internal_dns, local_ip)
  except:
    print "Error: Can't get local ip"

def get_external_ip():
  try:
    site = urllib.urlopen("http://curlmyip.com").read()
    grab = re.findall('\d{2,3}.\d{2,3}.\d{2,3}.\d{2,3}',site)
    external_ip = grab[0]
    dns_name(external_dns, external_ip)
  except:
    print "Error: Can't get external ip"

def conn(access_key, secret_key, region):
  ses = Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=region)
  return ses.client('route53')

def dns_name(dns, ip):
    try:
        route53 = conn(access_key,secret_key, region)
        response = route53.change_resource_record_sets(
          HostedZoneId=hosted_zone,
          ChangeBatch={
            'Comment': 'Created by myPiip',
            'Changes': [
              {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                  'Name': dns,
                  'Type': 'A',
                  'TTL': 600,
                  'ResourceRecords': [
                    {
                      'Value': ip
                    },
                  ],
                }
              },
            ]
          }
        )
        print "%s:%s" % (dns,ip)
    except:
        print "Error: Can't modify dns name"

def main():
    get_local_ip(ifname)
    get_external_ip()

parser       = ConfigParser.ConfigParser()
config       = parser.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), '.', 'mypiip.ini'))
access_key   = parser.get('config', 'access_key')
secret_key   = parser.get('config', 'secret_key')
hosted_zone  = parser.get('config', 'hosted_zone')
region       = parser.get('config', 'region')
ifname       = parser.get('config', 'ifname')
internal_dns = parser.get('config', 'internal_dns')
external_dns = parser.get('config', 'external_dns')

if __name__ == "__main__":
    main()
