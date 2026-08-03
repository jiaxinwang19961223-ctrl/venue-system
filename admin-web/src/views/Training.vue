<template>
  <div class="training-page">
    <el-tabs v-model="activeTab" type="border-card">
      <!-- ── 人脸消课 ── -->
      <el-tab-pane label="人脸消课" name="face">
        <div class="tab-hd">
          <span style="color:#909399;font-size:13px">当前场馆：<strong>{{ venueStore.currentName || '未选择' }}</strong></span>
        </div>
        <el-row :gutter="20">
          <el-col :span="10">
            <div class="face-main">
              <el-select v-model="faceCourseId" placeholder="选择课程" style="width:100%;margin-bottom:12px" @change="loadFaceStudents">
                <el-option v-for="c in courses" :key="c.id" :label="c.name+' · '+c.coach" :value="c.id" />
              </el-select>
              <div class="face-cam-big">
                <video ref="faceVideo2" autoplay playsinline width="360" height="270"></video>
                <canvas ref="faceCanvas2" width="360" height="270" style="position:absolute;top:-9999px"></canvas>
              </div>
              <div style="margin-top:12px;text-align:center">
                <el-button type="primary" size="large" @click="startFaceCamera2" :disabled="faceCameraOn2" :loading="faceLoading">
                  {{ faceCameraOn2 ? '摄像头已开' : '打开摄像头' }}
                </el-button>
                <el-button type="success" size="large" @click="startFaceCheckin" :disabled="!faceCameraOn2||!faceCourseId" :loading="faceDetecting2">
                  {{ faceDetecting2 ? '识别中...' : '开始签到' }}
                </el-button>
              </div>
              <p v-if="faceStatus2" :style="{color:faceOk2?'#67C23A':'#E6A23C',textAlign:'center',marginTop:'8px'}">{{ faceStatus2 }}</p>
            </div>
          </el-col>
          <el-col :span="14">
            <div class="face-result">
              <p style="font-weight:600;margin-bottom:12px">签到记录</p>
              <el-timeline v-if="faceLogs.length">
                <el-timeline-item v-for="log in faceLogs" :key="log.id" :timestamp="log.time" placement="top" :type="log.status==='success'?'success':'danger'">
                  <el-avatar v-if="log.face" :src="log.face" :size="28" shape="square" style="vertical-align:middle;margin-right:6px" />
                  <span :style="{color:log.status==='success'?'#67C23A':'#F56C6C'}">{{ log.name }}</span>
                  <span style="color:#909399;font-size:12px;margin-left:8px">{{ log.course_name }} · 剩余{{ log.remaining }}课时</span>
                </el-timeline-item>
              </el-timeline>
              <div v-else style="text-align:center;padding:40px 0;color:#C0C4CC">
                <i class="ri-camera-line" style="font-size:48px"></i>
                <p>人脸识别签到记录将显示在这里</p>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-tab-pane>

      <!-- ── 学员列表 ── -->
      <el-tab-pane label="学员列表" name="allStudents">
        <div class="tab-hd">
          <span style="color:#909399;font-size:13px">当前场馆：<strong>{{ venueStore.currentName || '未选择' }}</strong></span>
          <span style="color:#909399;font-size:12px">共 {{ allStudents.length }} 名学员</span>
        </div>
        <el-table :data="allStudents" stripe size="small" v-loading="allStudentsLoading">
          <el-table-column label="" width="50">
            <template #default="{ row }">
              <el-avatar v-if="row.member_face" :src="row.member_face" :size="32" shape="square" style="cursor:pointer" @click="previewFace(row.member_face, row.member_name)" />
              <el-avatar v-else :size="32" shape="square" style="background:#C0C4CC"><i class="ri-user-line"></i></el-avatar>
            </template>
          </el-table-column>
          <el-table-column prop="member_name" label="姓名" width="80" />
          <el-table-column prop="member_gender" label="性别" width="60" />
          <el-table-column label="年龄" width="60" align="center">
            <template #default="{ row }">{{ calcAge(row.member_birthday) || '—' }}</template>
          </el-table-column>
          <el-table-column prop="member_phone" label="手机号" width="130" />
          <el-table-column label="所属班级" min-width="130">
            <template #default="{ row }">
              <el-tag size="small" type="success">{{ row.course_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="消课进度" width="150">
            <template #default="{ row }">
              <el-progress :percentage="row.total_sessions?Math.round(row.used_sessions/row.total_sessions*100):0" :stroke-width="6" :color="row.used_sessions>=row.total_sessions?'#67C23A':'#409EFF'" />
              <span style="font-size:11px;color:#909399;margin-left:6px">{{ row.used_sessions }}/{{ row.total_sessions }}</span>
            </template>
          </el-table-column>
          <el-table-column label="入营时间" width="110">
            <template #default="{ row }">{{ row.enrolled_date || '—' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" type="primary" @click="editStudent(row)">编辑</el-button>
              <el-button size="small" type="warning" @click="showTransfer(row)">调班</el-button>
              <el-popconfirm title="移出课程？" @confirm="doUnenroll(row.id)"><template #reference><el-button size="small" type="danger" text>移出</el-button></template></el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!allStudentsLoading && !allStudents.length" description="暂无学员" :image-size="60" />
      </el-tab-pane>

      <!-- ── 课程管理 ── -->
      <el-tab-pane label="课程管理" name="list">
        <div class="tab-hd">
          <span style="color:#909399;font-size:13px">当前场馆：<strong>{{ venueStore.currentName || '未选择' }}</strong></span>
          <el-button type="primary" @click="showAddCourse" :disabled="!venueStore.currentId">新增课程</el-button>
        </div>
        <el-table :data="courses" stripe v-loading="loading">
          <el-table-column prop="name" label="课程名称" min-width="140" />
          <el-table-column label="教练" width="110">
            <template #default="{ row }">
              <el-avatar v-if="row.coach_face" :src="row.coach_face" :size="28" shape="circle" style="vertical-align:middle;margin-right:4px;cursor:pointer" @click="previewCoachFace(row)" />
              <el-avatar v-else :size="28" shape="circle" style="background:#409EFF;font-size:12px;vertical-align:middle;margin-right:4px">{{ row.coach?.[0] || '教' }}</el-avatar>
              {{ row.coach }}
            </template>
          </el-table-column>
          <el-table-column label="人数" width="80" align="center">
            <template #default="{ row }">{{ row.student_count }}/{{ row.max_students }}</template>
          </el-table-column>
          <el-table-column label="课时" width="70" align="center">
            <template #default="{ row }">{{ row.total_sessions }}节</template>
          </el-table-column>
          <el-table-column label="单价" width="90">
            <template #default="{ row }">¥{{ row.price_per_session }}/节</template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="{ row }">
              <el-button size="small" @click="showStudents(row)">学员</el-button>
              <el-button size="small" type="success" @click="showSessions(row)">消课</el-button>
              <el-button size="small" type="primary" @click="editCourse(row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!courses.length&&!loading" description="暂无课程" :image-size="60" />

        <el-dialog :title="editingCourseId?'编辑课程':'新增课程'" v-model="showCourseDialog" width="680px" @closed="stopCoachFaceCamera">
          <el-row :gutter="16">
            <el-col :span="14">
          <el-form :model="courseForm" label-width="80px">
            <el-form-item label="名称"><el-input v-model="courseForm.name" /></el-form-item>
            <el-form-item label="教练">
              <el-select v-model="courseForm.coach" style="width:100%" allow-create filterable placeholder="选择或输入教练">
                <el-option v-for="c in coachList" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
            <el-row :gutter="12">
              <el-col :span="12"><el-form-item label="人数"><el-input-number v-model="courseForm.max_students" :min="1" style="width:100%" /></el-form-item></el-col>
              <el-col :span="12"><el-form-item label="单价"><el-input-number v-model="courseForm.price_per_session" :min="0" :precision="2" style="width:100%" /></el-form-item></el-col>
            </el-row>
            <el-form-item label="描述"><el-input v-model="courseForm.description" type="textarea" rows="2" /></el-form-item>
          </el-form>
            </el-col>
            <el-col :span="10">
              <div class="face-capture">
                <p style="font-size:13px;font-weight:600;margin-bottom:8px">📷 教练人脸</p>
                <div class="face-cam-small">
                  <video ref="coachFaceVideo" autoplay playsinline width="320" height="240"></video>
                  <canvas ref="coachFaceCanvas" width="320" height="240" style="position:absolute;top:-9999px"></canvas>
                  <img v-if="coachFacePreview" :src="coachFacePreview" class="face-preview-small" />
                </div>
                <div style="margin-top:8px;display:flex;gap:6px;justify-content:center">
                  <el-button size="small" @click="openCoachFaceCamera" :disabled="coachFaceCameraOn">打开</el-button>
                  <el-button size="small" type="success" @click="captureCoachFace" :disabled="!coachFaceCameraOn">拍照</el-button>
                  <el-button size="small" v-if="coachFacePreview" @click="retakeCoachFace">重拍</el-button>
                </div>
                <p v-if="coachFaceStatus" style="font-size:11px;text-align:center;margin-top:4px" :style="{color:coachFaceOk?'#67C23A':'#E6A23C'}">{{ coachFaceStatus }}</p>
              </div>
            </el-col>
          </el-row>
          <template #footer><el-button @click="showCourseDialog=false">取消</el-button><el-button type="primary" @click="saveCourse">保存</el-button></template>
        </el-dialog>
      </el-tab-pane>

      <!-- ── 学员分班 ── -->
      <el-tab-pane label="学员分班" name="students">
        <div v-if="!selectedCourse" style="text-align:center;padding:60px 0;color:#909399">请在课程管理中点击「学员」按钮</div>
        <div v-else>
          <div class="tab-hd">
            <span><strong>{{ selectedCourse.name }}</strong> · {{ selectedCourse.coach }} · {{ selectedCourse.student_count }}/{{ selectedCourse.max_students }}人</span>
            <el-button size="small" @click="selectedCourse=null;activeTab='list'">← 返回</el-button>
          </div>
          <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center">
            <el-select v-model="enrollMemberId" filterable remote :remote-method="searchMembers" placeholder="搜索会员" style="width:220px" clearable>
              <el-option v-for="m in memberOptions" :key="m.id" :label="m.name+' '+m.phone" :value="m.id" />
            </el-select>
            <el-button type="primary" size="small" @click="doEnroll" :disabled="!enrollMemberId">加入课程</el-button>
            <el-button type="success" size="small" @click="showAddStudent">+ 新增学员</el-button>
          </div>

          <!-- 新增学员弹窗 -->
          <el-dialog title="新增学员" v-model="showStudentDialog" width="680px" @closed="stopNewFaceCamera">
            <el-row :gutter="16">
              <el-col :span="14">
            <el-form :model="studentForm" label-width="80px">
              <el-form-item label="姓名"><el-input v-model="studentForm.name" /></el-form-item>
              <el-form-item label="手机号"><el-input v-model="studentForm.phone" /></el-form-item>
              <el-row :gutter="12">
                <el-col :span="12"><el-form-item label="性别">
                  <el-select v-model="studentForm.gender" style="width:100%"><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select>
                </el-form-item></el-col>
                <el-col :span="12"><el-form-item label="生日">
                  <el-date-picker v-model="studentForm.birthday" type="date" value-format="YYYY-MM-DD" style="width:100%" />
                </el-form-item></el-col>
              </el-row>
              <el-form-item label="报名课时"><el-input-number v-model="studentForm.sessions" :min="1" :max="selectedCourse?.total_sessions||99" style="width:100%" /></el-form-item>
            </el-form>
              </el-col>
              <el-col :span="10">
                <div class="face-capture">
                  <p style="font-size:13px;font-weight:600;margin-bottom:8px">📷 人脸录入</p>
                  <div class="face-cam-small">
                    <video ref="newFaceVideo" autoplay playsinline width="320" height="240"></video>
                    <canvas ref="newFaceCanvas" width="320" height="240" style="position:absolute;top:-9999px"></canvas>
                    <img v-if="newFacePreview" :src="newFacePreview" class="face-preview-small" />
                  </div>
                  <div style="margin-top:8px;display:flex;gap:6px;justify-content:center">
                    <el-button size="small" @click="openNewFaceCamera" :disabled="newFaceCameraOn">打开</el-button>
                    <el-button size="small" type="success" @click="captureNewFace" :disabled="!newFaceCameraOn">拍照</el-button>
                    <el-button size="small" v-if="newFacePreview" @click="retakeNewFace">重拍</el-button>
                  </div>
                  <p v-if="newFaceStatus" style="font-size:11px;text-align:center;margin-top:4px" :style="{color:newFaceOk?'#67C23A':'#E6A23C'}">{{ newFaceStatus }}</p>
                </div>
              </el-col>
            </el-row>
            <template #footer><el-button @click="showStudentDialog=false">取消</el-button><el-button type="primary" @click="doAddStudent">创建并加入课程</el-button></template>
          </el-dialog>
          <el-table :data="students" stripe size="small">
            <el-table-column label="" width="50">
              <template #default="{ row }">
                <el-avatar v-if="row.member_face" :src="row.member_face" :size="32" shape="square" style="cursor:pointer" @click="previewFace(row.member_face, row.member_name)" />
                <el-avatar v-else :size="32" shape="square" style="background:#C0C4CC"><i class="ri-user-line"></i></el-avatar>
              </template>
            </el-table-column>
            <el-table-column prop="member_name" label="姓名" width="80" />
            <el-table-column prop="member_gender" label="性别" width="60" />
            <el-table-column label="入营时间" width="110">
              <template #default="{ row }">{{ row.enrolled_date || '—' }}</template>
            </el-table-column>
            <el-table-column label="年龄" width="60" align="center">
              <template #default="{ row }">{{ calcAge(row.member_birthday) || '—' }}岁</template>
            </el-table-column>
            <el-table-column prop="member_phone" label="手机号" width="130" />
            <el-table-column label="消课进度" width="180">
              <template #default="{ row }">
                <el-progress :percentage="row.total_sessions?Math.round(row.used_sessions/row.total_sessions*100):0" :stroke-width="8" :color="row.used_sessions>=row.total_sessions?'#67C23A':'#409EFF'" />
                <span style="font-size:12px;color:#909399;margin-left:8px">{{ row.used_sessions }}/{{ row.total_sessions }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="editStudent(row)">编辑</el-button>
                <el-popconfirm title="移出课程？" @confirm="doUnenroll(row.id)"><template #reference><el-button size="small" type="danger" text>移出</el-button></template></el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>

      </el-tab-pane>

      <!-- ── 消课考勤 ── -->
      <el-tab-pane label="消课考勤" name="sessions">
        <div v-if="!selectedCourse2" style="text-align:center;padding:60px 0;color:#909399">请在课程管理中点击「消课」按钮</div>
        <div v-else>
          <div class="tab-hd">
            <span><strong>{{ selectedCourse2.name }}</strong></span>
            <div>
              <el-button type="primary" size="small" @click="showAddSession">新增上课记录</el-button>
              <el-button size="small" @click="selectedCourse2=null;activeTab='list'">← 返回</el-button>
            </div>
          </div>
          <el-table :data="sessions" stripe size="small">
            <el-table-column prop="session_date" label="日期" width="110" />
            <el-table-column label="时间" width="120"><template #default="{ row }">{{ row.start_time }}-{{ row.end_time }}</template></el-table-column>
            <el-table-column prop="coach" label="教练" width="80" />
            <el-table-column prop="notes" label="备注" min-width="100" />
            <el-table-column label="考勤" width="80" align="center"><template #default="{ row }">{{ row.attendance_rate }}</template></el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button size="small" type="primary" @click="showAttendance(row)">签到</el-button>
                <el-popconfirm title="删除？" @confirm="deleteSession(row.id)"><template #reference><el-button size="small" type="danger" text>删除</el-button></template></el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <el-dialog title="新增上课" v-model="showSessionDialog" width="400px">
          <el-form :model="sessionForm" label-width="60px">
            <el-form-item label="日期"><el-date-picker v-model="sessionForm.session_date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
            <el-row :gutter="8">
              <el-col :span="10"><el-time-select v-model="sessionForm.start_time" start="06:00" step="01:00" end="23:00" style="width:100%" /></el-col>
              <el-col :span="4" style="text-align:center;line-height:32px;color:#909399">至</el-col>
              <el-col :span="10"><el-time-select v-model="sessionForm.end_time" start="06:00" step="01:00" end="23:00" style="width:100%" /></el-col>
            </el-row>
            <el-form-item label="教练" style="margin-top:12px"><el-input v-model="sessionForm.coach" /></el-form-item>
            <el-form-item label="备注"><el-input v-model="sessionForm.notes" /></el-form-item>
          </el-form>
          <template #footer><el-button @click="showSessionDialog=false">取消</el-button><el-button type="primary" @click="saveSession">创建并生成签到表</el-button></template>
        </el-dialog>

        <el-dialog title="考勤签到" v-model="showAttDialog" width="720px">
          <el-row :gutter="16">
            <el-col :span="14">
          <p style="margin-bottom:12px;color:#606266">{{ attSession?.session_date }} {{ attSession?.start_time }}-{{ attSession?.end_time }}</p>
          <el-table :data="attendances" stripe size="small" max-height="360">
            <el-table-column label="" width="50">
              <template #default="{ row }">
                <el-avatar v-if="row.member_face" :src="row.member_face" :size="32" shape="square" style="cursor:pointer" @click="previewFace(row.member_face, row.member_name)" />
                <el-avatar v-else :size="32" shape="square" style="background:#C0C4CC"><i class="ri-user-line"></i></el-avatar>
              </template>
            </el-table-column>
            <el-table-column prop="member_name" label="学员" width="80" />
            <el-table-column label="年龄" width="60" align="center">
              <template #default="{ row }">{{ calcAge(row.member_birthday) || '—' }}</template>
            </el-table-column>
            <el-table-column label="考勤" width="200">
              <template #default="{ row }">
                <el-radio-group v-model="row._status" size="small">
                  <el-radio-button label="present">✅ 到场</el-radio-button>
                  <el-radio-button label="absent">❌ 缺席</el-radio-button>
                  <el-radio-button label="late">⏰ 迟到</el-radio-button>
                </el-radio-group>
              </template>
            </el-table-column>
            <el-table-column label="备注" min-width="100">
              <template #default="{ row }"><el-input v-model="row._notes" size="small" placeholder="原因" /></template>
            </el-table-column>
          </el-table>
            </el-col>
            <!-- 人脸签到 -->
            <el-col :span="10">
              <div class="face-checkin-mini">
                <p style="font-weight:600;margin-bottom:8px;font-size:13px">📷 人脸签到</p>
                <div class="face-cam-mini">
                  <video ref="faceVideo" autoplay playsinline width="200" height="150"></video>
                  <canvas ref="faceCanvas" width="200" height="150" style="position:absolute;top:-9999px"></canvas>
                </div>
                <div style="margin-top:8px">
                  <el-button size="small" @click="startFaceCamera" :disabled="faceCameraOn">打开摄像头</el-button>
                  <el-button size="small" type="success" @click="startFaceDetect" :disabled="!faceCameraOn||faceDetecting">{{ faceDetecting?'识别中...':'开始识别' }}</el-button>
                </div>
                <p v-if="faceStatus" :style="{color:faceOk?'#67C23A':'#E6A23C',fontSize:'12px',marginTop:'8px'}">{{ faceStatus }}</p>
                <div v-if="faceMatched" class="face-match-result">
                  <el-avatar :src="faceMatched.member_face" :size="40" shape="square" />
                  <div>
                    <strong>{{ faceMatched.member_name }}</strong>
                    <p style="font-size:12px;color:#67C23A;margin:0">✅ 已签到</p>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
          <template #footer><el-button @click="showAttDialog=false">取消</el-button><el-button type="primary" @click="saveAttendance">保存并消课</el-button></template>
        </el-dialog>
      </el-tab-pane>

      <!-- ── 信息管理 ── -->
      <el-tab-pane label="信息管理" name="logs">
        <div class="tab-hd">
          <span style="color:#909399;font-size:13px">当前场馆：<strong>{{ venueStore.currentName || '未选择' }}</strong></span>
        </div>
        <el-tabs v-model="logTab" type="card" size="small" style="margin-top:8px">
          <el-tab-pane label="消费记录" name="orders">
            <el-table :data="trainingOrders" stripe size="small" v-loading="logLoading" max-height="500">
              <el-table-column prop="order_no" label="订单号" width="170" />
              <el-table-column prop="name" label="学员" width="80" />
              <el-table-column label="类型" width="80"><template #default="{ row }">{{ row.type_label }}</template></el-table-column>
              <el-table-column label="时间" width="155">
                <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace('T',' ') }}</template>
              </el-table-column>
              <el-table-column label="金额" width="90">
                <template #default="{ row }"><span :style="{ color: row.status==='refunded'?'#67C23A':'#F56C6C' }">{{ row.status==='refunded'?'+':'−' }}¥{{ Math.abs(row.paid_amount||0).toFixed(2) }}</span></template>
              </el-table-column>
              <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
            </el-table>
            <el-empty v-if="!logLoading&&!trainingOrders.length" description="暂无记录" :image-size="60" />
          </el-tab-pane>
          <el-tab-pane label="修改记录" name="modifications">
            <el-table :data="modifications" stripe size="small" v-loading="logLoading2">
              <el-table-column label="时间" width="155">
                <template #default="{ row }">{{ row.created_at?.slice(0,16)?.replace('T',' ') }}</template>
              </el-table-column>
              <el-table-column prop="student_name" label="学员" width="80" />
              <el-table-column prop="field" label="修改字段" width="100" />
              <el-table-column label="变更" width="200">
                <template #default="{ row }"><span style="color:#909399">{{ row.old_value }}</span> → <span style="color:#409EFF">{{ row.new_value }}</span></template>
              </el-table-column>
              <el-table-column prop="operator" label="操作人" width="80" />
              <el-table-column prop="remark" label="备注" min-width="100" />
            </el-table>
            <el-empty v-if="!logLoading2&&!modifications.length" description="暂无记录" :image-size="60" />
          </el-tab-pane>
        </el-tabs>
      </el-tab-pane>
    </el-tabs>

    <!-- 编辑学员弹窗（全局，各Tab共用） -->
    <el-dialog title="编辑学员" v-model="showEditStudentDialog" width="680px" @closed="stopEditFaceCamera">
      <el-row :gutter="16">
        <el-col :span="14">
      <el-form :model="editStudentForm" label-width="80px">
        <el-form-item label="姓名"><el-input v-model="editStudentForm.name" /></el-form-item>
        <el-form-item label="手机号"><el-input v-model="editStudentForm.phone" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="性别">
            <el-select v-model="editStudentForm.gender" style="width:100%"><el-option label="男" value="男" /><el-option label="女" value="女" /></el-select>
          </el-form-item></el-col>
          <el-col :span="12"><el-form-item label="生日">
            <el-date-picker v-model="editStudentForm.birthday" type="date" value-format="YYYY-MM-DD" style="width:100%" />
          </el-form-item></el-col>
        </el-row>
        <el-form-item label="报名课时"><el-input-number v-model="editStudentForm.sessions" :min="1" style="width:100%" /></el-form-item>
      </el-form>
        </el-col>
        <el-col :span="10">
          <div class="face-capture">
            <p style="font-size:13px;font-weight:600;margin-bottom:8px">📷 人脸</p>
            <div class="face-cam-small">
              <video ref="editFaceVideo" autoplay playsinline width="320" height="240"></video>
              <canvas ref="editFaceCanvas" width="320" height="240" style="position:absolute;top:-9999px"></canvas>
              <img v-if="editFacePreview" :src="editFacePreview" class="face-preview-small" />
            </div>
            <div style="margin-top:8px;display:flex;gap:6px;justify-content:center">
              <el-button size="small" @click="openEditFaceCamera" :disabled="editFaceCameraOn">打开</el-button>
              <el-button size="small" type="success" @click="captureEditFace" :disabled="!editFaceCameraOn">拍照</el-button>
              <el-button size="small" v-if="editFacePreview" @click="retakeEditFace">重拍</el-button>
            </div>
            <p v-if="editFaceStatus" style="font-size:11px;text-align:center;margin-top:4px" :style="{color:editFaceOk?'#67C23A':'#E6A23C'}">{{ editFaceStatus }}</p>
          </div>
        </el-col>
      </el-row>
      <template #footer><el-button @click="showEditStudentDialog=false">取消</el-button><el-button type="primary" @click="doEditStudent">保存</el-button></template>
    </el-dialog>

    <!-- 班级调整弹窗 -->
    <el-dialog title="调整班级" v-model="showTransferDialog" width="420px">
      <p style="margin-bottom:12px"><strong>{{ transferStudent?.member_name }}</strong> · 当前：<el-tag size="small" type="success">{{ transferStudent?.course_name }}</el-tag></p>
      <el-form label-width="80px">
        <el-form-item label="转入班级">
          <el-select v-model="transferCourseId" style="width:100%" placeholder="选择目标课程">
            <el-option v-for="c in transferCourses" :key="c.id" :label="c.name + ' · ' + c.coach" :value="c.id" />
          </el-select>
        </el-form-item>
        <p style="font-size:12px;color:#909399">课时数将平移（{{ transferStudent?.total_sessions || 0 }}课时）</p>
      </el-form>
      <template #footer><el-button @click="showTransferDialog=false">取消</el-button><el-button type="primary" @click="doTransfer">确认调班</el-button></template>
    </el-dialog>

    <!-- 照片预览 -->
    <el-dialog :title="coachPreview?.name || '照片'" v-model="showCoachPreview" width="360px" @closed="coachPreview=null">
      <img v-if="coachPreview" :src="coachPreview.src" style="max-width:100%;max-height:400px;border-radius:8px;object-fit:contain;display:block;margin:0 auto" />
      <p v-if="coachPreview?.name" style="text-align:center;margin-top:8px;color:#606266">{{ coachPreview.name }}</p>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import api from '../api'
import { useVenueStore } from '../stores/venue'
import { ElMessage } from 'element-plus'

const venueStore = useVenueStore()
const activeTab = ref('list')
const courses = ref([])
const coachList = computed(() => [...new Set(courses.value.map(c => c.coach).filter(Boolean))].sort())
const loading = ref(false)
// 信息管理
const logTab = ref('orders')
const trainingOrders = ref([])
const modifications = ref([])
const logLoading = ref(false)
const logLoading2 = ref(false)
// 汇总学员列表
const allStudents = ref([])
const allStudentsLoading = ref(false)

// 课程
const showCourseDialog = ref(false)
const editingCourseId = ref(null)
const courseForm = ref({ name:'', coach:'', max_students:20, total_sessions:10, price_per_session:0, description:'', coach_face:null })
// 教练人脸
const coachFaceVideo = ref(null); const coachFaceCanvas = ref(null)
const coachFaceCameraOn = ref(false); const coachFacePreview = ref(null)
const coachFaceStatus = ref(''); const coachFaceOk = ref(false)
let coachFaceStream = null
const coachPreview = ref(null)
const showCoachPreview = ref(false)

// 学员
const selectedCourse = ref(null)
const students = ref([])
const enrollMemberId = ref(null)
const memberOptions = ref([])
const showStudentDialog = ref(false)
const studentForm = ref({ name:'', phone:'', gender:'男', birthday:'', sessions:10 })
// 新增学员人脸
const newFaceVideo = ref(null)
const newFaceCanvas = ref(null)
const newFaceCameraOn = ref(false)
const newFacePreview = ref(null)
const newFaceDescriptor = ref(null)
const newFaceStatus = ref('')
const newFaceOk = ref(false)
let newFaceStream = null
// 编辑学员
const showEditStudentDialog = ref(false)
const editStudentForm = ref({ member_id:null, enrollment_id:null, name:'', phone:'', gender:'男', birthday:'', sessions:10 })
const editFaceVideo = ref(null); const editFaceCanvas = ref(null)
const editFaceCameraOn = ref(false); const editFacePreview = ref(null)
const editFaceDescriptor = ref(null); const editFaceStatus = ref(''); const editFaceOk = ref(false)
let editFaceStream = null
// 班级调整
const showTransferDialog = ref(false)
const transferStudent = ref(null)
const transferCourseId = ref(null)
const transferCourses = ref([])
watch(showTransferDialog, (v) => {
  if (v && transferStudent.value) {
    const curId = transferStudent.value.course_id
    transferCourses.value = (courses.value || []).filter(c => c.id !== curId)
  }
})

// 消课
const selectedCourse2 = ref(null)
const sessions = ref([])
const showSessionDialog = ref(false)
const sessionForm = ref({ course_id:null, session_date:'', start_time:'09:00', end_time:'10:00', coach:'', notes:'' })
const showAttDialog = ref(false)
const attSession = ref(null)
const attendances = ref([])

// 人脸消课（主Tab）
const faceCourseId = ref(null)
const faceVideo2 = ref(null)
const faceCanvas2 = ref(null)
const faceCameraOn2 = ref(false)
const faceDetecting2 = ref(false)
const faceStatus2 = ref('')
const faceOk2 = ref(false)
const faceLoading = ref(false)
const faceLogs = ref([])
const faceStudents = ref([])
let faceStream2 = null
let faceInterval2 = null

// 人脸签到（考勤弹窗）
const faceVideo = ref(null)
const faceCanvas = ref(null)
const faceCameraOn = ref(false)
const faceDetecting = ref(false)
const faceStatus = ref('')
const faceOk = ref(false)
const faceMatched = ref(null)
let faceStream = null
let faceInterval = null
let faceDescriptors = []

async function startFaceCamera() {
  try {
    faceStream = await navigator.mediaDevices.getUserMedia({ video: { width: 200, height: 150, facingMode: 'user' } })
    if (faceVideo.value) faceVideo.value.srcObject = faceStream
    faceCameraOn.value = true; faceStatus.value = '摄像头就绪，点击开始识别'
  } catch { faceStatus.value = '摄像头不可用'; faceOk.value = false }
}

async function startFaceDetect() {
  faceDetecting.value = true; faceStatus.value = '加载人脸模型...'
  try {
    // 加载模型
    const { default: faceapi } = await import('face-api.js')
    const M = '/models'
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(M),
      faceapi.nets.faceLandmark68TinyNet.loadFromUri(M),
      faceapi.nets.faceRecognitionNet.loadFromUri(M),
    ])
    faceStatus.value = '准备学员人脸数据...'
    // 加载当前课程学员的人脸
    const labeledDescs = []
    for (const s of attendances.value) {
      try {
        const mRes = await api.get(`/members/${s.member_id || s.enrollment_id}`)
        if (mRes?.face_descriptor) {
          const desc = new Float32Array(JSON.parse(mRes.face_descriptor))
          labeledDescs.push(new faceapi.LabeledFaceDescriptors(s.member_name, [desc]))
        }
      } catch { /* */ }
    }
    if (!labeledDescs.length) { faceStatus.value = '没有学员录入过人脸'; faceDetecting.value = false; return }
    const matcher = new faceapi.FaceMatcher(labeledDescs, 0.5)
    faceStatus.value = '请正对摄像头...'

    faceInterval = setInterval(async () => {
      if (!faceVideo.value || faceVideo.value.readyState < 2) return
      const result = await faceapi.detectSingleFace(faceVideo.value, new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.4 }))
        .withFaceLandmarks(true).withFaceDescriptor()
      if (!result) return
      const match = matcher.findBestMatch(result.descriptor)
      if (match.label !== 'unknown') {
        faceStatus.value = `识别到: ${match.label}`
        faceOk.value = true
        // 自动标记到场
        const att = attendances.value.find(a => a.member_name === match.label)
        if (att) { att._status = 'present'; faceMatched.value = att }
        clearInterval(faceInterval)
        faceDetecting.value = false
      }
    }, 1500)
  } catch (e) {
    faceStatus.value = '模型加载失败'; faceOk.value = false; faceDetecting.value = false
  }
}

function stopFaceCamera() {
  if (faceStream) { faceStream.getTracks().forEach(t => t.stop()); faceStream = null }
  if (faceInterval) { clearInterval(faceInterval); faceInterval = null }
  faceCameraOn.value = false; faceDetecting.value = false
  faceMatched.value = null; faceOk.value = false
}

// ═══ 人脸消课主功能 ═══
async function loadFaceStudents() {
  if (!faceCourseId.value) return
  try { faceStudents.value = (await api.get(`/courses/${faceCourseId.value}/students`)).students || [] } catch { /* */ }
}

async function startFaceCamera2() {
  faceLoading.value = true
  try {
    faceStream2 = await navigator.mediaDevices.getUserMedia({ video: { width: 360, height: 270, facingMode: 'user' } })
    if (faceVideo2.value) faceVideo2.value.srcObject = faceStream2
    faceCameraOn2.value = true; faceStatus2.value = '摄像头就绪'
  } catch { faceStatus2.value = '摄像头不可用' }
  faceLoading.value = false
}

async function startFaceCheckin() {
  faceDetecting2.value = true; faceStatus2.value = '加载模型...'
  try {
    const { default: faceapi } = await import('face-api.js')
    const M = '/models'
    await Promise.all([
      faceapi.nets.tinyFaceDetector.loadFromUri(M),
      faceapi.nets.faceLandmark68TinyNet.loadFromUri(M),
      faceapi.nets.faceRecognitionNet.loadFromUri(M),
    ])
    // 加载已报名学员的人脸
    await loadFaceStudents()
    const labeled = []
    for (const s of faceStudents.value) {
      try {
        const mRes = await api.get(`/members/${s.member_id}`)
        if (mRes?.face_descriptor) {
          const desc = new Float32Array(JSON.parse(mRes.face_descriptor))
          labeled.push(new faceapi.LabeledFaceDescriptors(s.member_name, [desc]))
        }
      } catch { /* */ }
    }
    if (!labeled.length) { faceStatus2.value = '本课程没有学员录入过人脸'; faceDetecting2.value = false; return }
    const matcher = new faceapi.FaceMatcher(labeled, 0.5)
    faceStatus2.value = '请正对摄像头...'
    const checkedIds = new Set()

    faceInterval2 = setInterval(async () => {
      if (!faceVideo2.value || faceVideo2.value.readyState < 2) return
      const result = await faceapi.detectSingleFace(faceVideo2.value, new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.4 }))
        .withFaceLandmarks(true).withFaceDescriptor()
      if (!result) return
      const match = matcher.findBestMatch(result.descriptor)
      if (match.label === 'unknown') return

      const student = faceStudents.value.find(s => s.member_name === match.label)
      if (!student || checkedIds.has(student.id)) return
      checkedIds.add(student.id)

      // 自动创建上课记录+签到+消课
      const now = new Date()
      const today = now.toISOString().slice(0,10)
      const time = `${String(now.getHours()).padStart(2,'0')}:00`
      try {
        const sRes = await api.post('/courses/sessions', {
          course_id: faceCourseId.value,
          session_date: today, start_time: time,
          end_time: `${String(now.getHours()+1).padStart(2,'0')}:00`,
          notes: '人脸签到自动消课',
        })
        if (sRes?.id) {
          const aRes = await api.get(`/courses/sessions/${sRes.id}/attendance`)
          const atts = (aRes.attendances || []).map(a => ({
            enrollment_id: a.enrollment_id,
            status: a.enrollment_id === student.id ? 'present' : 'absent',
            notes: a.enrollment_id === student.id ? '人脸签到' : '',
          }))
          await api.put(`/courses/sessions/${sRes.id}/attendance`, { session_id: sRes.id, attendances: atts })
        }
      } catch(e) { console.error(e) }

      faceLogs.value.unshift({
        id: Date.now(), name: match.label,
        face: student.member_face, status: 'success',
        course_name: courses.value.find(c=>c.id===faceCourseId.value)?.name||'',
        remaining: student.total_sessions - student.used_sessions - 1,
        time: `${today} ${time}`,
      })
      faceStatus2.value = `✅ ${match.label} 签到成功！`
      faceOk2.value = true
      setTimeout(() => { faceOk2.value = false; faceStatus2.value = '请正对摄像头...' }, 3000)
    }, 2000)
  } catch (e) {
    faceStatus2.value = '模型加载失败'; faceDetecting2.value = false
  }
}

function stopFaceCamera2() {
  if (faceStream2) { faceStream2.getTracks().forEach(t => t.stop()); faceStream2 = null }
  if (faceInterval2) { clearInterval(faceInterval2); faceInterval2 = null }
  faceCameraOn2.value = false; faceDetecting2.value = false
}

function calcAge(birthday) {
  if (!birthday) return null
  const b = new Date(birthday)
  const now = new Date()
  let age = now.getFullYear() - b.getFullYear()
  if (now.getMonth() < b.getMonth() || (now.getMonth() === b.getMonth() && now.getDate() < b.getDate())) age--
  return age
}

async function loadCourses() {
  if (!venueStore.currentId) { courses.value = []; return }
  loading.value = true
  try { courses.value = (await api.get('/courses', { params: { venue_id: venueStore.currentId } })).courses || [] }
  catch { /* */ }
  loading.value = false
}

async function loadAllStudents() {
  if (!venueStore.currentId) { allStudents.value = []; return }
  allStudentsLoading.value = true
  try {
    const cs = (await api.get('/courses', { params: { venue_id: venueStore.currentId } })).courses || []
    const list = []
    for (const c of cs) {
      try {
        const ss = (await api.get(`/courses/${c.id}/students`)).students || []
        for (const s of ss) list.push({ ...s, course_name: c.name, course_id: c.id })
      } catch { /* */ }
    }
    allStudents.value = list
  } catch { /* */ }
  allStudentsLoading.value = false
}

function showAddCourse() { editingCourseId.value = null; courseForm.value = { name:'', coach:'', max_students:20, total_sessions:10, price_per_session:0, description:'', coach_face:null }; coachFacePreview.value = null; showCourseDialog.value = true }
function editCourse(row) { editingCourseId.value = row.id; courseForm.value = { ...row }; coachFacePreview.value = row.coach_face || null; showCourseDialog.value = true }
async function saveCourse() {
  if (!courseForm.value.name) { ElMessage.warning('请输入课程名称'); return }
  try {
    const d = { ...courseForm.value, venue_id: venueStore.currentId, coach_face: coachFacePreview.value || courseForm.value.coach_face }
    editingCourseId.value ? await api.put(`/courses/${editingCourseId.value}`, d) : await api.post('/courses', d)
    showCourseDialog.value = false; await loadCourses(); ElMessage.success('保存成功')
  } catch { /* */ }
}
async function deleteCourse(id) { try { await api.delete(`/courses/${id}`); await loadCourses(); ElMessage.success('已停用') } catch { /* */ } }

async function showStudents(row) { selectedCourse.value = row; activeTab.value = 'students'; try { students.value = (await api.get(`/courses/${row.id}/students`)).students || [] } catch { /* */ } }
async function searchMembers(q) {
  if (!q || q.length < 2) { memberOptions.value = []; return }
  try { const r = await api.get('/members', { params: { keyword: q, venue_id: venueStore.currentId } }); memberOptions.value = r.members || [] } catch { /* */ }
}
async function doEnroll() {
  try { await api.post('/courses/enroll', { course_id: selectedCourse.value.id, member_id: enrollMemberId.value, total_sessions: selectedCourse.value.total_sessions }); enrollMemberId.value = null; await showStudents(selectedCourse.value); await loadAllStudents(); ElMessage.success('已加入') } catch { /* */ }
}
function showAddStudent() {
  studentForm.value = { name:'', phone:'', gender:'男', birthday:'', sessions: selectedCourse.value?.total_sessions||10 }
  showStudentDialog.value = true
}
async function doAddStudent() {
  if (!studentForm.value.name || !studentForm.value.phone) { ElMessage.warning('请填写姓名和手机号'); return }
  try {
    const studentData = {
      venue_id: venueStore.currentId,
      name: studentForm.value.name,
      phone: studentForm.value.phone,
      gender: studentForm.value.gender,
      birthday: studentForm.value.birthday || null,
    }
    if (newFacePreview.value) {
      studentData.face_image = newFacePreview.value
      studentData.face_descriptor = newFaceDescriptor.value || null
    }
    const mRes = await api.post('/courses/students', studentData)
    if (mRes?.id) {
      await api.post('/courses/enroll', {
        course_id: selectedCourse.value.id,
        member_id: mRes.id,
        total_sessions: studentForm.value.sessions,
      })
    }
    stopNewFaceCamera()
    showStudentDialog.value = false
    await showStudents(selectedCourse.value)
    await loadAllStudents()
    ElMessage.success('学员已创建并加入课程')
  } catch { /* */ }
}

// 新学员人脸拍照
async function openNewFaceCamera() {
  try {
    newFaceStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } })
    if (newFaceVideo.value) newFaceVideo.value.srcObject = newFaceStream
    newFaceCameraOn.value = true
  } catch { newFaceStatus.value = '摄像头不可用' }
}
async function captureNewFace() {
  const video = newFaceVideo.value; const canvas = newFaceCanvas.value
  if (!video || !canvas || video.readyState < 2) { newFaceStatus.value = '摄像头未就绪'; return }
  canvas.width = video.videoWidth || 640; canvas.height = video.videoHeight || 480
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
  newFacePreview.value = canvas.toDataURL('image/jpeg', 1.0)
  if (newFaceStream) { newFaceStream.getTracks().forEach(t => t.stop()); newFaceStream = null }
  newFaceCameraOn.value = false; newFaceStatus.value = '提取人脸...'
  try {
    const { default: faceapi } = await import('face-api.js')
    await Promise.all([faceapi.nets.tinyFaceDetector.loadFromUri('/models'), faceapi.nets.faceLandmark68TinyNet.loadFromUri('/models'), faceapi.nets.faceRecognitionNet.loadFromUri('/models')])
    const d = await faceapi.detectSingleFace(canvas, new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.4 })).withFaceLandmarks(true).withFaceDescriptor()
    if (d) { newFaceDescriptor.value = JSON.stringify(Array.from(d.descriptor)); newFaceStatus.value = '✅ 已提取'; newFaceOk.value = true }
    else { newFaceStatus.value = '⚠ 未检测到人脸'; newFaceOk.value = false }
  } catch { newFaceStatus.value = '仅照片'; newFaceOk.value = false }
}
function retakeNewFace() {
  if (newFaceStream) { newFaceStream.getTracks().forEach(t => t.stop()); newFaceStream = null }
  newFaceCameraOn.value = false
  newFacePreview.value = null; newFaceDescriptor.value = null
  newFaceStatus.value = ''; newFaceOk.value = false
  setTimeout(() => openNewFaceCamera(), 300)
}
// 编辑学员
async function editStudent(row) {
  editStudentForm.value = {
    member_id: row.member_id, enrollment_id: row.id,
    name: row.member_name||'', phone: row.member_phone||'',
    gender: row.member_gender||'男', birthday: row.member_birthday||'',
    sessions: row.total_sessions,
  }
  editFacePreview.value = row.member_face || null
  editFaceDescriptor.value = null; editFaceStatus.value = row.member_face?'已有照片':''
  showEditStudentDialog.value = true
}
async function doEditStudent() {
  if (!editStudentForm.value.name) { ElMessage.warning('请输入姓名'); return }
  try {
    await api.put(`/members/${editStudentForm.value.member_id}`, {
      name: editStudentForm.value.name,
      phone: editStudentForm.value.phone,
      gender: editStudentForm.value.gender,
      birthday: editStudentForm.value.birthday || null,
    })
    // 更新课时数（可选）
    if (editStudentForm.value.enrollment_id) {
      try { await api.put(`/courses/enroll/${editStudentForm.value.enrollment_id}`, { total_sessions: editStudentForm.value.sessions, course_id: 0, member_id: 0 }) } catch { /* */ }
    }
    stopEditFaceCamera(); showEditStudentDialog.value = false
    if (selectedCourse.value) await showStudents(selectedCourse.value)
    await loadAllStudents(); ElMessage.success('已更新')
  } catch (e) {
    console.error('编辑失败', e)
    ElMessage.error('保存失败')
  }
}
async function openEditFaceCamera() {
  try {
    editFaceStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } })
    if (editFaceVideo.value) editFaceVideo.value.srcObject = editFaceStream
    editFaceCameraOn.value = true
  } catch { editFaceStatus.value = '不可用' }
}
async function captureEditFace() {
  const video = editFaceVideo.value; const canvas = editFaceCanvas.value
  if (!video || !canvas || video.readyState < 2) { editFaceStatus.value = '未就绪'; return }
  canvas.width = video.videoWidth || 640; canvas.height = video.videoHeight || 480
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
  const img = canvas.toDataURL('image/jpeg', 1.0)
  editFacePreview.value = img
  if (editFaceStream) { editFaceStream.getTracks().forEach(t => t.stop()); editFaceStream = null }
  editFaceCameraOn.value = false; editFaceStatus.value = '提取特征...'
  let desc = null
  try {
    const { default: faceapi } = await import('face-api.js')
    await Promise.all([faceapi.nets.tinyFaceDetector.loadFromUri('/models'), faceapi.nets.faceLandmark68TinyNet.loadFromUri('/models'), faceapi.nets.faceRecognitionNet.loadFromUri('/models')])
    const d = await faceapi.detectSingleFace(canvas, new faceapi.TinyFaceDetectorOptions({ inputSize: 320, scoreThreshold: 0.4 })).withFaceLandmarks(true).withFaceDescriptor()
    if (d) { desc = JSON.stringify(Array.from(d.descriptor)); editFaceDescriptor.value = desc; editFaceStatus.value = '✅ 人脸已更新'; editFaceOk.value = true }
    else { editFaceStatus.value = '⚠ 未检测到人脸'; editFaceOk.value = false }
  } catch { editFaceStatus.value = '照片已更新'; editFaceOk.value = false }
  // 直接保存人脸到后端
  const mid = editStudentForm.value.member_id
  if (mid && mid > 0) {
    try {
      await api.put(`/members/${mid}`, {
        face_image: img, face_descriptor: desc,
      })
      editFaceStatus.value = '✅ 人脸已更新'
    } catch (e) {
      console.error('人脸保存失败', e)
      editFaceStatus.value = '保存失败'
    }
  } else {
    editFaceStatus.value = '⚠ 请先填写信息并保存后再拍照'
  }
}
function retakeEditFace() {
  if (editFaceStream) { editFaceStream.getTracks().forEach(t => t.stop()); editFaceStream = null }
  editFaceCameraOn.value = false
  editFacePreview.value = null; editFaceDescriptor.value = null
  editFaceStatus.value = ''; editFaceOk.value = false
  setTimeout(() => openEditFaceCamera(), 300)
}
function stopEditFaceCamera() {
  if (editFaceStream) { editFaceStream.getTracks().forEach(t => t.stop()); editFaceStream = null }
  editFaceCameraOn.value = false; editFacePreview.value = null; editFaceDescriptor.value = null; editFaceStatus.value = ''; editFaceOk.value = false
}

// 教练人脸
async function openCoachFaceCamera() {
  try {
    coachFaceStream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: 'user' } })
    if (coachFaceVideo.value) coachFaceVideo.value.srcObject = coachFaceStream
    coachFaceCameraOn.value = true
  } catch { coachFaceStatus.value = '不可用' }
}
async function captureCoachFace() {
  const video = coachFaceVideo.value; const canvas = coachFaceCanvas.value
  if (!video || !canvas || video.readyState < 2) { coachFaceStatus.value = '未就绪'; return }
  canvas.width = video.videoWidth || 640; canvas.height = video.videoHeight || 480
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height)
  coachFacePreview.value = canvas.toDataURL('image/jpeg', 1.0)
  if (coachFaceStream) { coachFaceStream.getTracks().forEach(t => t.stop()); coachFaceStream = null }
  coachFaceCameraOn.value = false; coachFaceStatus.value = '✅ 已拍照'
}
function retakeCoachFace() {
  if (coachFaceStream) { coachFaceStream.getTracks().forEach(t => t.stop()); coachFaceStream = null }
  coachFaceCameraOn.value = false; coachFacePreview.value = null; coachFaceStatus.value = ''
  setTimeout(() => openCoachFaceCamera(), 300)
}
function previewCoachFace(row) {
  if (row.coach_face) { coachPreview.value = { name: row.coach, src: row.coach_face }; showCoachPreview.value = true }
}
function previewFace(src, name) {
  if (src) { coachPreview.value = { name: name || '', src }; showCoachPreview.value = true }
}
function stopCoachFaceCamera() {
  if (coachFaceStream) { coachFaceStream.getTracks().forEach(t => t.stop()); coachFaceStream = null }
  coachFaceCameraOn.value = false; coachFacePreview.value = null; coachFaceStatus.value = ''
}

function stopNewFaceCamera() {
  if (newFaceStream) { newFaceStream.getTracks().forEach(t => t.stop()); newFaceStream = null }
  newFaceCameraOn.value = false; newFacePreview.value = null; newFaceDescriptor.value = null; newFaceStatus.value = ''; newFaceOk.value = false
}
async function doUnenroll(id) { try { await api.delete(`/courses/enroll/${id}`); if (selectedCourse.value) await showStudents(selectedCourse.value); await loadAllStudents(); ElMessage.success('已移出') } catch { /* */ } }
function showTransfer(row) {
  transferStudent.value = row
  transferCourseId.value = null
  showTransferDialog.value = true
}
async function doTransfer() {
  if (!transferCourseId.value) { ElMessage.warning('请选择目标班级'); return }
  try {
    await api.delete(`/courses/enroll/${transferStudent.value.id}`)
    await api.post('/courses/enroll', {
      course_id: transferCourseId.value,
      member_id: transferStudent.value.member_id,
      total_sessions: transferStudent.value.total_sessions,
    })
    showTransferDialog.value = false
    if (selectedCourse.value) await showStudents(selectedCourse.value)
    await loadAllStudents()
    await loadCourses()
    ElMessage.success('调班成功')
  } catch { /* */ }
}

async function showSessions(row) { selectedCourse2.value = row; activeTab.value = 'sessions'; await loadSessions() }
async function loadSessions() { try { sessions.value = (await api.get(`/courses/${selectedCourse2.value.id}/sessions`)).sessions || [] } catch { /* */ } }
function showAddSession() { sessionForm.value = { course_id: selectedCourse2.value.id, session_date: new Date().toISOString().slice(0,10), start_time:'09:00', end_time:'10:00', coach: selectedCourse2.value.coach||'', notes:'' }; showSessionDialog.value = true }
async function saveSession() { try { await api.post('/courses/sessions', sessionForm.value); showSessionDialog.value = false; await loadSessions(); ElMessage.success('已创建') } catch { /* */ } }
async function deleteSession(id) { try { await api.delete(`/courses/sessions/${id}`); await loadSessions(); ElMessage.success('已删除') } catch { /* */ } }

async function showAttendance(row) {
  attSession.value = row
  stopFaceCamera(); faceStatus.value = ''; faceMatched.value = null
  try {
    const r = await api.get(`/courses/sessions/${row.id}/attendance`)
    attendances.value = (r.attendances || []).map(a => ({ ...a, _status: a.status, _notes: a.notes || '' }))
  } catch { /* */ }
  showAttDialog.value = true
}
async function saveAttendance() {
  try {
    await api.put(`/courses/sessions/${attSession.value.id}/attendance`, {
      session_id: attSession.value.id,
      attendances: attendances.value.map(a => ({ enrollment_id: a.enrollment_id, status: a._status, notes: a._notes }))
    })
    showAttDialog.value = false; await loadSessions(); ElMessage.success('签到已保存，已自动消课')
  } catch { /* */ }
}

async function loadTrainingLogs() {
  if (!venueStore.currentId) return
  logLoading.value = true
  try {
    const allOrders = []
    for (const c of courses.value) {
      try {
        const ss = (await api.get(`/courses/${c.id}/sessions`)).sessions || []
        for (const s of ss) {
          const attR = await api.get(`/courses/sessions/${s.id}/attendance`)
          const atts = attR.attendances || []
          for (const a of atts) {
            if (a.status === 'present') {
              allOrders.push({
                order_no: 'T'+String(s.id).padStart(4,'0'),
                name: a.member_name,
                type_label: '消课',
                created_at: s.session_date + ' ' + s.start_time,
                paid_amount: c.price_per_session || 0,
                status: 'checked_in',
                remark: c.name + ' · ' + s.notes,
              })
            }
          }
        }
      } catch { /* */ }
    }
    trainingOrders.value = allOrders.sort((a,b) => (b.created_at||'').localeCompare(a.created_at||''))
  } catch { /* */ }
  logLoading.value = false
}

// 修改记录（简化版）
async function loadModifications() {
  logLoading2.value = true
  try {
    const logs = []
    for (const c of courses.value) {
      try {
        const ss = (await api.get(`/courses/${c.id}/students`)).students || []
        for (const s of ss) {
          if (s.enrolled_date) {
            logs.push({
              created_at: s.enrolled_date,
              student_name: s.member_name,
              field: '报名',
              old_value: '-',
              new_value: `加入「${c.name}」`,
              operator: '管理员',
              remark: `${s.total_sessions}课时`,
            })
          }
        }
      } catch { /* */ }
    }
    modifications.value = logs.sort((a,b) => (b.created_at||'').localeCompare(a.created_at||''))
  } catch { /* */ }
  logLoading2.value = false
}

onMounted(async () => { await venueStore.load(); await loadCourses(); await loadAllStudents() })
watch(() => venueStore.currentId, () => { loadCourses(); loadAllStudents() })
watch(activeTab, (v) => {
  if (v === 'logs') { loadTrainingLogs(); loadModifications() }
})
watch(showAttDialog, (v) => { if (!v) stopFaceCamera() })
watch(activeTab, (v) => { if (v !== 'face') stopFaceCamera2() })
</script>

<style scoped>
.training-page { max-width: 1200px; }
.tab-hd { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; gap: 12px; }
:deep(.el-tabs__content) { padding: 20px; }
.face-checkin-mini { background: #FAFAFA; border: 1px solid #EBEEF5; border-radius: 8px; padding: 12px; text-align: center; }
.face-cam-mini { width: 200px; height: 150px; margin: 0 auto; background: #000; border-radius: 4px; overflow: hidden; }
.face-cam-mini video { width: 100%; height: 100%; object-fit: cover; }
.face-match-result { display: flex; align-items: center; gap: 10px; padding: 8px; background: #F0F9EB; border-radius: 8px; margin-top: 8px; }
.face-main { padding: 8px; }
.face-cam-big { width: 360px; height: 270px; margin: 0 auto; background: #000; border-radius: 8px; overflow: hidden; }
.face-cam-big video { width: 100%; height: 100%; object-fit: cover; }
.face-result { max-height: 400px; overflow-y: auto; }
.face-capture { background: #FAFAFA; border: 1px dashed #DCDFE6; border-radius: 8px; padding: 10px; text-align: center; }
.face-cam-small { width: 320px; height: 240px; margin: 0 auto; background: #000; border-radius: 4px; overflow: hidden; position: relative; }
.face-cam-small video, .face-preview-small { width: 100%; height: 100%; object-fit: cover; }
</style>
