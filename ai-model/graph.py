import matplotlib.pyplot as plt

epochs = list(range(1, 11))

train_acc = [0.6515, 0.7867, 0.8254, 0.8491, 0.8645, 0.8738, 0.8831, 0.8901, 0.8950, 0.9012]
val_acc   = [0.7598, 0.8322, 0.8349, 0.8384, 0.8556, 0.8666, 0.8593, 0.8652, 0.8591, 0.8689]

plt.figure()
plt.plot(epochs, train_acc, label="Training Accuracy")
plt.plot(epochs, val_acc, label="Validation Accuracy")

plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.title("Model Accuracy Graph")
plt.legend()

plt.savefig("accuracy_graph.png")
plt.show()