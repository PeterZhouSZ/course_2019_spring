%% system parameters
n = 200;
A = 0.99;
Q = 5;
C1 = 2;
R1 = 5;
C2 = 2 * ones(1,2);
R2 = 5 * eye(2);
C4 = 2 * ones(1,4);
R4 = 5 * eye(4);
C5 = 2 * ones(1,5);
R5 = 5 * eye(5);

%% initial state
x0 = 1;
P0 = 1;
x = zeros(n+1,1);
y = zeros(n+1,5);
x(1) = x0;
% estimator 1
x1 = zeros(n+1,1);
P1 = zeros(n+1,1);
x1(1) = x0;
P1(1) = P0;
% estimator 2
x2 = zeros(n+1,1);
P2 = zeros(n+1,1);
x2(1) = x0;
P2(1) = P0;

%% measurement y
for i = 1:n
    w = wgn(1,1,5);
    x(i+1) = A * x(i) + w;
    v = wgn(1,5,5);
    y(i+1,:) = C5 * x(i+1) + v;
end

%% esimator 1
for i = 1:n
    % when t-2, 5 sensor measurement
    if i > 2
        [x1(i-1), P1(i-1)] = KalmanFilter(x1(i-2), y(i-1, :), P1(i-2), A, C5, R5, Q);
    end
    % t-1, 4 sensor measurement
    if i > 1
        [x1(i), P1(i)] = KalmanFilter(x1(i-1), y(i, 1:4), P1(i-1), A, C4, R4, Q);
    end
    % t, 1 sensor measurement
    [x1(i+1), P1(i+1)] = KalmanFilter(x1(i), y(i+1, 1), P1(i), A, C1, R1, Q);
end

for i = 1:n
    % t-1, 5 sensor measurement
    if i > 1
        [x2(i), P1(i)] = KalmanFilter(x2(i-1), y(i, :), P2(i-1), A, C5, R5, Q);
    end
    % t, 2 sensor measurement
    [x2(i+1), P2(i+1)] = KalmanFilter(x2(i), y(i+1, 1:2), P2(i), A, C2, R2, Q);
end

t = 1:n;
figure;
plot(t, x(t+1), 'b');
hold on
plot(t, x1(t+1), 'g--');
hold on
plot(t, x2(t+1), 'r*');
hold on
legend('x', 'x1', 'x2');

%% solve dare
P = dare(A, C5, Q, R5);         % steady state
P1 = P - P * C4 * inv(C4' * P * C4 + R4) * C4' * P;
P1 = A * P1 * A' + Q;
P1 = P1 - P1 * C1 * inv(C1' * P1 * C1 + R1) * C1' * P1;
P2 = P - P * C2 * inv(C2' * P * C2 + R2) * C2' * P;




    