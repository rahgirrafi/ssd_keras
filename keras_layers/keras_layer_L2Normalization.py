'''
A custom Keras layer to perform L2-normalization.

Copyright (C) 2018 Pierluigi Ferrari

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from __future__ import division
import numpy as np
import keras.backend as K 
from keras.layers import Layer, InputSpec
import tensorflow as tf

class L2Normalization(Layer):
    '''
    Performs L2 normalization on the input tensor with a learnable scaling parameter
    as described in the paper "Parsenet: Looking Wider to See Better" (see references)
    and as used in the original SSD model.

    Arguments:
        gamma_init (int): The initial scaling parameter. Defaults to 20 following the
            SSD paper.

    Input shape:
        4D tensor of shape `(batch, channels, height, width)` if `dim_ordering = 'th'`
        or `(batch, height, width, channels)` if `dim_ordering = 'tf'`.

    Returns:
        The scaled tensor. Same shape as the input tensor.

    References:
        http://cs.unc.edu/~wliu/papers/parsenet.pdf
    '''

    def __init__(self, gamma_init=20, **kwargs):
       # CORRECTED: Use proper Keras image format check
       if K.image_data_format() == 'channels_last':
           self.axis = -1  # More robust way to specify last axis
       else:
           self.axis = 1
       self.gamma_init = gamma_init
       super(L2Normalization, self).__init__(**kwargs)

    def build(self, input_shape):
        self.input_spec = [InputSpec(shape=input_shape)]
        # PROPERLY register the gamma parameter using add_weight()
        self.gamma = self.add_weight(
            name='gamma', 
            shape=(input_shape[self.axis],),
            initializer=tf.constant_initializer(self.gamma_init),
            trainable=True
        )
        super(L2Normalization, self).build(input_shape)

    def call(self, x, mask=None):
        output = tf.math.l2_normalize(x, self.axis)
        print(output, self.gamma)
        return output * self.gamma

    def get_config(self):
        config = {
            'gamma_init': self.gamma_init
        }
        base_config = super(L2Normalization, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))
