import numpy as np
import tensorflow as tf

# Example dataset
X = np.array([1, 2, 3, 4, 5])
y = np.array([2, 3, 4, 5, 6])

# Define the model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(units=1, input_shape=[1])
])

# Compile the model
model.compile(optimizer='sgd', loss='mean_squared_error')

# Train the model
model.fit(X, y, epochs=1000, verbose=0)

# Predict the output
predictions = model.predict(X)
print("Predictions:", predictions.flatten())

