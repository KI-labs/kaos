# frozen_string_literal: true

require 'awspec'
require 'aws-sdk'
require 'rhcl'

vpc_name = "kaos-2-test-vpc"
state_file = 'terraform.tfstate.d/kitchen-terraform-default-aws/terraform.tfstate'
tf_state = JSON.parse(File.open(state_file).read)
eip = nil
nat_id = nil

tf_state['modules'].each do |val|
 if val['path'].length == 2
    if val['path'][1] == 'storage'
        ENV['AWS_REGION'] = val['outputs']['region']['value']
    elsif val['path'][1] == 'network'
        eip = val['resources']['aws_eip.nat']['primary']['attributes']['public_ip']
        nat_id = val['resources']['aws_nat_gateway.this']['primary']['attributes']['id']
    end
 end
end


ec2 = Aws::EC2::Client.new(region: ENV['AWS_REGION'])
azs = ec2.describe_availability_zones
zone_names = azs.to_h[:availability_zones].first(2).map { |az| az[:zone_name] }

describe vpc(vpc_name.to_s) do
  it { should exist }
  it { should be_available }
  it { should have_tag('project').value('kaos') }
  it { should have_tag('env').value('test') }
  it { should have_tag('version').value('2') }
  it { should have_route_table("#{vpc_name}-public") }
  it { should have_route_table("#{vpc_name}-private") }
end

zone_names.each do |az|
  describe subnet("#{vpc_name}-public-#{az}") do
    it { should exist }
    it { should be_available }
    it { should belong_to_vpc(vpc_name.to_s) }
    it { should have_tag('project').value('kaos') }
    it { should have_tag('env').value('test') }
    it { should have_tag('version').value('2') }
  end
  describe subnet("#{vpc_name}-private-#{az}") do
    it { should exist }
    it { should be_available }
    it { should belong_to_vpc(vpc_name.to_s) }
    it { should have_tag('project').value('kaos') }
    it { should have_tag('env').value('test') }
    it { should have_tag('version').value('2') }
  end
end

describe eip(eip.to_s) do
  it { should exist }
end

describe nat_gateway(nat_id.to_s) do
  it { should exist }
  it { should be_available }
  it { should have_eip(eip.to_s) }
  it { should belong_to_vpc(vpc_name.to_s) }
end