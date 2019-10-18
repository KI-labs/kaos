# encoding: utf-8
# copyright: 2019, KI labs

title 'kaos storage integration tests'

env = ENV["ENVIRONMENT"]
store_name =  env.nil? || env.empty? || env == 'prod' ? 'kaos-2-store' : "kaos-2-#{env}-store"

describe google_storage_bucket(name: store_name) do
  it { should exist }
  its('name') { should eq store_name  }
  its('location') { should eq 'EU'  }
end