function [x_next, P_next] = KalmanFilter(x, y, P, A, C, R, Q)
    x_ = A * x;
    P_ = A * P * A' + Q;
    k = P * C * inv(C' * P_ * C + R);
    x_next = x_ + k * (y - C * x_)';
    P_next = P_ - k * C' * P_;
end