# encoding: utf-8
# copyright: 2019, KI labs

title 'kaos kubernetes network integration tests'

gcp_project_id = attribute('gcp_project_id')

env = ENV["ENVIRONMENT"]
network_name =  env.nil? || env.empty? || env == 'prod' ? 'kaos-2-vnet' : "kaos-2-#{env}-vnet"
subnetwork_name =  env.nil? || env.empty? || env == 'prod' ? 'kaos-2-vnet-k8s-subnetwork' : "kaos-2-#{env}-vnet-k8s-subnetwork"

describe google_compute_network(project: gcp_project_id,  name: network_name) do
  it { should exist }
  its('name') { should eq network_name }
  its ('auto_create_subnetworks'){ should be false }
  its ('subnetworks.count') { should eq 1 }
  its ('subnetworks.first') { should match subnetwork_name}
end
