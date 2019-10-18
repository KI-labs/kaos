# encoding: utf-8
# copyright: 2019, KI labs

title 'kaos kubernetes cluster integration tests'

gcp_project_id = attribute('gcp_project_id')

env = ENV["ENVIRONMENT"]
cluster_name =  env.nil? || env.empty? || env == 'prod' ? 'kaos-2' : "kaos-2-#{env}"
network_name =  env.nil? || env.empty? || env == 'prod' ? 'kaos-2-vnet' : "kaos-2-#{env}-vnet"
subnetwork_name =  env.nil? || env.empty? || env == 'prod' ? 'kaos-2-vnet-k8s-subnetwork' : "kaos-2-#{env}-vnet-k8s-subnetwork"


describe google_container_regional_cluster(project: gcp_project_id, name: cluster_name, location: 'europe-west3') do
  it {should exist}
  its('location') {should eq 'europe-west3'}
end


describe google_container_regional_cluster(project: gcp_project_id, name: cluster_name, location: 'europe-west3') do
  its('network') {should eq network_name}
  its('subnetwork') {should eq subnetwork_name}
end

describe google_container_regional_node_pool(project: gcp_project_id, name: cluster_name, location: 'europe-west3', cluster: cluster_name) do
  its('initial_node_count') {should eq 1}
end