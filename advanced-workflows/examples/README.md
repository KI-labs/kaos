# Examples

{% hint style="info" %}
All examples herein use the same [Quick Start](../../getting-started/quick-start.md) **MNIST** model for simplicity
{% endhint %}

## Problem Definition

> To train a machine learning model to classify images based on the MNIST dataset.

The trained model should be able to classify incoming images into 10 categories \(0 to 9\) based on its learning from the [MNIST dataset](./#mnist-dataset). Finally, the trained model must be able to correctly identify the digit represented in a newly created image \(i.e. an image the model has never seen\).

## MNIST Dataset

The [MNIST dataset](http://yann.lecun.com/exdb/mnist/) contains a large number of images of hand-written digits in the range 0 to 9, as well as the labels identifying the digit in each image. The dataset is split in three parts.

* 55,000 examples of training data
* 10,000 examples of test data
* 5,000 examples of validation data

{% hint style="danger" %}
The current template consists of an **abbreviated set** \(15%\) of the original MNIST dataset
{% endhint %}

## Model Architecture

{% hint style="info" %}
The basic MNIST template model is available via `kaos template`
{% endhint %}

The template model is a mixture of seven distinct layers.

* 2 x convolution
* 2 x max pooling
* 2 x dense \(fully connected\)
* 1 x dropout

